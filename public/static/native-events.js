document.addEventListener('DOMContentLoaded', () => {
  const root = document.querySelector('.resume-content-box');
  if (root) {
    const templateId = root.dataset.templateId || '';

    // 使用此模版
    root.querySelectorAll('[data-action="useTemplate"]').forEach((el) => {
      el.addEventListener('click', () => {
        if (!templateId) return;
        window.location.href = `/designResume/${templateId}`;
      });
    });

    // 点击分类标签跳转
    root.querySelectorAll('[data-action="clickTag"]').forEach((el) => {
      el.style.cursor = 'pointer';
      el.addEventListener('click', () => {
        const key = el.dataset.key;
        const value = el.dataset.value;
        if (!key || !value) return;

        const params = new URLSearchParams();
        params.set(value, key);
        window.location.href = `/resume?${params.toString()}`;
      });
    });

    // 查看更多模版
    root.querySelectorAll('[data-action="toMore"]').forEach((el) => {
      el.style.cursor = 'pointer';
      el.addEventListener('click', () => {
        window.location.href = '/resume';
      });
    });

    // 跳转至模版详情
    root.querySelectorAll('[data-action="toResumeDetail"]').forEach((el) => {
      el.style.cursor = 'pointer';
      el.addEventListener('click', () => {
        const id = el.dataset.id;
        if (!id) return;
        window.open(`/resumedetail/${id}`, '_blank');
      });
    });
  }

  // logo 点击事件
  const logo = document.getElementById('logo');
  if (logo) {
    logo.addEventListener('click', () => {
      window.location.href = '/';
    });
  }
});
