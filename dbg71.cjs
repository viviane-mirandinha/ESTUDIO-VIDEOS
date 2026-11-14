const puppeteer=require('puppeteer-core');
(async()=>{
 const b=await puppeteer.launch({executablePath:process.argv[2],headless:'shell',args:['--no-sandbox','--allow-file-access-from-files']});
 const p=await b.newPage();
 p.on('pageerror',e=>console.log('PAGEERR',e.message,(e.stack||'').split('\n').slice(0,4).join('|')));
 p.on('console',m=>console.log('LOG',m.text()));
 await p.goto('file:///'+process.argv[3].replace(/\\/g,'/'),{waitUntil:'load'});
 await new Promise(r=>setTimeout(r,2500));
 await b.close();
})();
