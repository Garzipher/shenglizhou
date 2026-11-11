const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({headless:true, executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const page = await browser.newPage({ viewport:{width:1500,height:1200}, deviceScaleFactor:1 });
  await page.goto('http://127.0.0.1:8766/site/resume-gdry.html',{waitUntil:'networkidle'});
  await page.evaluate(() => {const sheet=document.querySelector('.resume-sheet');document.body.replaceChildren(sheet);});
  await page.addStyleTag({content:`@page{size:A4;margin:12mm 0} html,body{margin:0!important;padding:0!important;background:white!important} .resume-sheet[data-template="1"]{box-sizing:border-box!important;margin:0 auto!important;max-width:none!important;width:210mm!important;min-height:273mm!important;height:auto!important;box-shadow:none!important;border-left:0!important;border-right:0!important} .resume-sheet[data-template="1"] .resume-entry{break-inside:avoid} .resume-sheet[data-template="1"] .resume-section h2{break-after:avoid}`});
  await page.emulateMedia({media:'screen'});
  await page.pdf({path:'site/variants/gdry/Zhou_Shengli_Resume_GDRY_Template1.pdf',format:'A4',printBackground:true,preferCSSPageSize:true});
  await browser.close();
})();
