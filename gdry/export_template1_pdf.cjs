const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({headless:true, executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const page = await browser.newPage({ viewport:{width:1500,height:1200}, deviceScaleFactor:1 });
  await page.goto('http://127.0.0.1:8766/site/resume-gdry.html',{waitUntil:'networkidle'});
  await page.evaluate(() => {const sheet=document.querySelector('.resume-sheet');document.body.replaceChildren(sheet);});
  await page.addStyleTag({content:`@page{size:A4;margin:0} html,body{margin:0!important;padding:0!important;background:white!important} .resume-sheet[data-template="1"]{box-sizing:border-box!important;margin:0!important;max-width:none!important;width:210mm!important;height:297mm!important;min-height:297mm!important;box-shadow:none!important}`});
  await page.emulateMedia({media:'screen'});
  await page.pdf({path:'site/variants/gdry/Zhou_Shengli_Resume_GDRY_Template1.pdf',format:'A4',printBackground:true,preferCSSPageSize:true});
  await browser.close();
})();
