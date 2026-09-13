import { createServer } from "node:http";
import { readFile, realpath } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

// QA-only preview: loopback, read-only, prototype directory only, no API/proxy.
const root = path.dirname(fileURLToPath(import.meta.url));
const types = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".woff2": "font/woff2",
};
createServer(async (request, response) => {
  if (!["GET", "HEAD"].includes(request.method)) {
    response.writeHead(405).end();
    return;
  }
  try {
    const pathname = decodeURIComponent(
      new URL(request.url, "http://127.0.0.1").pathname,
    );
    const target = await realpath(
      path.join(
        root,
        pathname.endsWith("/") ? `${pathname}index.html` : pathname,
      ),
    );
    const relative = path.relative(root, target);
    if (
      relative.startsWith("..") ||
      path.isAbsolute(relative) ||
      !types[path.extname(target)]
    )
      throw new Error("Not public");
    const data = await readFile(target);
    response.writeHead(200, {
      "Content-Type": types[path.extname(target)],
      "Cache-Control": "no-store",
      "Referrer-Policy": "no-referrer",
      "X-Content-Type-Options": "nosniff",
    });
    response.end(request.method === "HEAD" ? undefined : data);
  } catch {
    response.writeHead(404).end("Not found");
  }
}).listen(Number(process.argv[2] || 0), "127.0.0.1", function () {
  console.log(`Prototype QA only: http://127.0.0.1:${this.address().port}`);
});
