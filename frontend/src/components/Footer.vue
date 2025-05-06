<template>
  <footer class="app-footer">
    <p>© 2025 半数黑金(Half_Black_Money). 版权所有.</p>
    <div class="footer-links">
      <a href="#">关于我们</a>
      <a href="#">联系方式</a>
      <a href="#">隐私政策</a>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  display: flex;
  justify-content: center; /* 修改为居中对齐 */
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background-color: #f5f5f5;
  border-top: 1px solid #ddd;
  width: 100%; /* 确保占据全宽 */
}

.footer-links {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}
</style>