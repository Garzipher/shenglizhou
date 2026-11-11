(() => {
  const select = document.getElementById('resume-template');
  const sheet = document.querySelector('.resume-sheet');
  const links = document.querySelectorAll('.resume-actions .resume-download');
  if (!select || !sheet || links.length !== 2) return;
  const files = {
    '1': ['Zhou_Shengli_Resume_GDRY_Template1.pdf', 'Zhou_Shengli_Resume_GDRY_Template1.docx'],
    '2': ['Zhou_Shengli_Resume_GDRY.pdf', 'Zhou_Shengli_Resume_GDRY.docx']
  };
  select.addEventListener('change', () => {
    const choice = files[select.value] ? select.value : '1';
    sheet.dataset.template = choice;
    links.forEach((link, index) => {
      link.href = 'variants/gdry/' + files[choice][index];
      link.download = '周圣力_个人简历_模板' + choice + (index ? '.docx' : '.pdf');
    });
  });
})();
