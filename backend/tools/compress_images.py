import os
from PIL import Image
from typing import List, Optional, Callable


class ImageCompressor:
    """图片压缩工具类，提供PNG和ICO格式的压缩功能"""
    
    def __init__(self, image_paths: Optional[List[str]] = None):
        """
        初始化图片压缩器
        
        Args:
            image_paths: 需要压缩的图片路径列表，默认为空
        """
        self.image_paths = image_paths or []
        self.logger: Optional[Callable[[str], None]] = None
    
    def set_logger(self, logger_func: Callable[[str], None]) -> None:
        """
        设置日志记录函数
        
        Args:
            logger_func: 接收字符串参数的日志记录函数
        """
        self.logger = logger_func
    
    def _log(self, message: str) -> None:
        """内部日志记录方法"""
        if self.logger:
            self.logger(message)
    
    def compress_images(self) -> None:
        """主程序逻辑：压缩指定的图片文件"""
        if not self.image_paths:
            self._log("没有指定需要压缩的图片文件")
            return
            
        for image_path in self.image_paths:
            if not os.path.exists(image_path):
                self._log(f"警告: 文件 {image_path} 不存在，跳过压缩。")
                continue
            
            try:
                if image_path.lower().endswith(".png"):
                    self._log(f"正在压缩 PNG: {image_path}")
                    self.compress_png(image_path)
                elif image_path.lower().endswith(".ico"):
                    self._log(f"正在压缩 ICO: {image_path}")
                    self.compress_ico(image_path)
                else:
                    self._log(f"未知的文件类型: {image_path}")
            except Exception as e:
                self._log(f"压缩失败 {image_path}: {e}")
        
        self._log("压缩完成。")
    
    def compress_png(self, image_path: str, colors: int = 256, method: int = 2, optimize: bool = True) -> None:
        """
        压缩PNG图片
        
        Args:
            image_path: 图片文件路径
            colors: 颜色数量，用于调色板量化
            method: 量化方法
            optimize: 是否启用优化
        """
        with Image.open(image_path) as img:
            # 转换为 RGBA 并简化调色板
            img = img.convert("RGBA")
            img = img.quantize(colors=colors, method=method)
            # 保存优化后的图片
            img.save(image_path, optimize=optimize)
    
    def compress_ico(self, image_path: str, sizes: Optional[List[int]] = None) -> None:
        """
        压缩ICO图标
        
        Args:
            image_path: 图标文件路径
            sizes: 不同DPI的尺寸列表
        """
        sizes = sizes or [16, 32, 48, 64, 128, 256]  # 默认尺寸
        
        with Image.open(image_path) as img:
            # 保留原始尺寸，采用默认质量进行重绘
            img.save(image_path, format="ICO", sizes=[(size, size) for size in sizes])


if __name__ == "__main__":
    # 默认要压缩的图片路径
    DEFAULT_IMAGES_TO_COMPRESS = [
        r"frontend\public\favicon.ico",
        r"frontend\src\assets\images\defcard.png",
        r"frontend\src\assets\images\logo.png"
    ]
    
    # 创建压缩器实例
    compressor = ImageCompressor(DEFAULT_IMAGES_TO_COMPRESS)
    
    # 设置简单的控制台日志输出
    import sys
    compressor.set_logger(lambda msg: print(f"[ImageCompressor] {msg}"))
    
    # 执行压缩
    compressor.compress_images()