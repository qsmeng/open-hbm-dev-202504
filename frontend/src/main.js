
// 初始化移动端适配
function initMobileAdaptation() {
  // 检测是否是移动设备
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  
  if (isMobile) {
    document.documentElement.classList.add('mobile');
    
    // 加载移动端专用CSS
    import('./assets/mobile.css');
    
    // 配置移动端专属设置
    configureMobileSettings();
  }
}

// 配置移动端专属设置
function configureMobileSettings() {
  // 优化滚动性能
  document.body.style.overflow = 'auto';
  
  // 启用快速点击
  FastClick.attach(document.body);
  
  // 调整视口缩放
  document.querySelector('meta[name="viewport"]').setAttribute(
    'content', 
    'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
  );
}
