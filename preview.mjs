import http from 'node:http';
import {readFileSync,statSync} from 'node:fs';
import path from 'node:path';
const args=process.argv;const port=Number(args[args.indexOf('--port')+1])||4173;
const root=path.resolve('dist');const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.webp':'image/webp','.png':'image/png','.svg':'image/svg+xml'};
http.createServer((req,res)=>{try{let url=decodeURIComponent(new URL(req.url,'http://preview').pathname);let file=path.resolve(root,'.'+url);if(!file.startsWith(root+path.sep)&&file!==root)throw Error();if(file===root||statMaybe(file)?.isDirectory())file=path.join(file,'index.html');if(!statMaybe(file)&&!path.extname(file))file+='.html';res.setHeader('Content-Type',types[path.extname(file)]||'application/octet-stream');res.end(readFileSync(file));}catch{res.statusCode=404;res.end('Not found');}}).listen(port,'0.0.0.0');
function statMaybe(p){try{return statSync(p)}catch{return null}}
