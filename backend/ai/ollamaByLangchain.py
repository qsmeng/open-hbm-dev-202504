"""
Ollama语言模型集成模块
=====================

使用LangChain框架集成Ollama语言模型，提供对话服务和故事生成功能。

主要功能:
- initialize_ollama_model: 初始化Ollama模型
- create_tools: 创建对话工具集
- main: 启动AI对话服务
- 测试函数: 验证各功能模块

依赖组件:
- Ollama: 本地运行的LLM服务
- LangChain: 对话链框架
- FastAPI: 提供API接口
- Uvicorn: ASGI服务器

环境要求:
- OLLAMA_BASE_URL: Ollama服务地址
- OLLAMA_MODEL_NAME: 使用的模型名称

安全注意事项:
1. 用户输入需进行验证和清理
2. 敏感操作需要认证
3. 生产环境应配置HTTPS
"""

def initialize_ollama_model(base_url: str, model_name: str) -> OllamaLLM:
    """
    初始化Ollama语言模型
    
    参数:
    - base_url: Ollama服务地址(如http://localhost:11434)
    - model_name: 模型名称(如llama2)
    
    返回值:
    - OllamaLLM: 初始化的模型实例
    
    异常:
    - HTTPException: 模型初始化失败时抛出500错误
    
    配置说明:
    - temperature: 控制生成随机性(0-1)
    - top_p: 核采样参数
    - timeout: 请求超时时间
    """
    try:
        llm = OllamaLLM(
            base_url=base_url,
            model=model_name,
            temperature=0.7,  # 中等随机性
            top_p=0.9,  # 高多样性
            timeout=DEFAULT_TIMEOUT
        )
        logger.info(f"成功初始化Ollama模型: {model_name}")
        return llm
    except Exception as e:
        logger.error(f"初始化Ollama模型失败: {e}")
        raise HTTPException(status_code=500, detail="模型初始化失败")

def create_tools() -> List[Tool]:
    """
    创建对话系统工具集
    
    返回值:
    - List[Tool]: LangChain工具列表
    
    工具说明:
    1. search: 信息搜索(待实现)
    2. calculator: 数学计算(需加强安全)
    3. story_generator: 故事生成
    4. dialogue_manager: 对话管理
    
    TODO:
    - 实现实际搜索功能
    - 加强计算器安全性
    """
    tools = [
        Tool(
            name="search",
            func=lambda query: "搜索结果",  # TODO: 替换为实际搜索实现 - 需要集成搜索引擎API
            description="用于搜索相关信息"
        ),
        Tool(
            name="calculator",
            func=lambda expr: str(eval(expr)),  # TODO: 使用更安全计算库 - 考虑使用ast.literal_eval或专用数学库
            description="用于执行数学计算"
        ),
        Tool(
            name="story_generator",
            func=lambda prompt: generate_story(prompt),
            description="用于生成故事内容"
        ),
        Tool(
            name="dialogue_manager",
            func=lambda message: manage_dialogue(message),
            description="用于管理对话流程"
        )
    ]
    return tools

def main():
    """
    启动AI对话服务
    
    流程:
    1. 初始化语言模型
    2. 加载提示模板
    3. 创建工具集
    4. 创建对话agent
    5. 启动FastAPI服务
    
    异常:
    - 启动失败会记录错误日志
    
    生产建议:
    - 使用Gunicorn多worker
    - 配置日志轮转
    """
    try:
        # 初始化Ollama语言模型
        llm = initialize_ollama_model(OLLAMA_BASE_URL, OLLAMA_MODEL_NAME)
        
        # 加载系统提示模板
        prompt = load_prompt_template()
        
        # 初始化对话工具
        tools = create_tools()
        
        # 创建对话agent
        agent = create_conversation_agent(llm, tools, prompt)
        
        # 配置FastAPI应用
        app = FastAPI()
        
        @app.post("/chat")
        async def chat_endpoint(request: Request):
            """处理用户聊天请求"""
            data = await request.json()
            user_input = data.get("message")
            if not user_input:
                raise HTTPException(status_code=400, detail="缺少消息内容")
            
            try:
                response = chat_with_agent(user_input, agent)
                return JSONResponse(content=response)
            except Exception as e:
                logger.error(f"对话处理失败: {e}")
                raise HTTPException(status_code=500, detail="对话处理失败")
        
        # 启动Uvicorn服务器
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise

def test_chat_with_agent():
    """
    测试对话agent功能
    
    测试点:
    - 模型初始化
    - 工具加载
    - 对话响应格式
    
    断言:
    - 响应为字典类型
    - 包含response字段
    - 响应内容非空
    """
    # 测试模型初始化
    llm = initialize_ollama_model(OLLAMA_BASE_URL, OLLAMA_MODEL_NAME)
    
    # 测试提示模板加载
    prompt = load_prompt_template()
    
    # 测试工具集创建
    tools = create_tools()
    
    # 测试agent创建
    agent = create_conversation_agent(llm, tools, prompt)
    
    # 测试对话功能
    test_message = "你好，你能帮我生成一个故事吗？"
    response = chat_with_agent(test_message, agent)
    
    assert isinstance(response, dict), "响应应为字典类型"
    assert "response" in response, "响应中应包含'response'字段"
    assert len(response["response"]) > 0, "响应内容不应为空"

def test_handle_generate_story():
    """
    测试故事生成功能
    
    测试点:
    - 故事主题处理
    - 角色列表处理
    - 生成故事格式
    
    断言:
    - 响应为字典类型
    - 包含story字段
    - 故事内容非空
    """
    theme = "冒险"  # 测试主题
    characters = ["英雄", "恶龙"]  # 测试角色
    
    response = handle_generate_story(theme, characters)
    
    assert isinstance(response, dict), "响应应为字典类型"
    assert "story" in response, "响应中应包含'story'字段"
    assert len(response["story"]) > 0, "故事内容不应为空"

def test_handle_manage_dialogue():
    """
    测试对话管理功能
    
    测试点:
    - 消息处理
    - 响应格式
    
    断言:
    - 响应为字典类型
    - 包含response字段
    - 响应内容非空
    """
    message = "你好，你能帮我生成一个故事吗？"  # 测试消息
    
    response = handle_manage_dialogue(message)
    
    assert isinstance(response, dict), "响应应为字典类型"
    assert "response" in response, "响应中应包含'response'字段"
    assert len(response["response"]) > 0, "响应内容不应为空"

if __name__ == "__main__":
    """模块直接执行时运行的测试"""
    test_chat_with_agent()
    test_handle_generate_story()
    test_handle_manage_dialogue()
    print("所有测试通过！")
