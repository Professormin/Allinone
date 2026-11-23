const copyButton = document.querySelector('#copy');
const phrase = document.querySelector('#phrase');
const feedback = document.querySelector('#feedback');

copyButton.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(phrase.value);
    feedback.textContent = '已复制安装话术。';
  } catch {
    phrase.focus();
    phrase.select();
    feedback.textContent = '已选中安装话术，请使用设备的复制功能。';
  }
});
