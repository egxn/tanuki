#!/usr/bin/env node
// Tanuki OpenCascade.js modules (*.js) -> STEP files.
// usage: node export_step.mjs <in_dir> <out_dir> [--single assembly.step]
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const [inDir, outDir, ...rest] = process.argv.slice(2);
if (!inDir || !outDir) {
  console.error("usage: node export_step.mjs <in_dir> <out_dir> [--single name.step]");
  process.exit(2);
}
const single = rest[0] === "--single" ? rest[1] : null;
fs.mkdirSync(outDir, { recursive: true });

import initOpenCascade from "opencascade.js/dist/node.js";
const oc = await initOpenCascade();

function writeStep(shape, file) {
  const writer = new oc.STEPControl_Writer_1();
  const status = writer.Transfer(shape, oc.STEPControl_StepModelType.STEPControl_AsIs, true, new oc.Message_ProgressRange_1());
  if (status !== oc.IFSelect_ReturnStatus.IFSelect_RetDone) throw new Error("STEP transfer failed");
  const tmp = "/tmp_" + path.basename(file);
  const w = writer.Write(tmp);
  if (w !== oc.IFSelect_ReturnStatus.IFSelect_RetDone) throw new Error("STEP write failed");
  fs.writeFileSync(file, oc.FS.readFile(tmp));
  oc.FS.unlink(tmp);
}

const files = fs.readdirSync(inDir).filter((f) => f.endsWith(".js")).sort();
const builder = new oc.BRep_Builder();
const assembly = new oc.TopoDS_Compound();
builder.MakeCompound(assembly);
let ok = 0, failed = [], warnings = [];
const f_name = (f) => f.replace(/_gen\.js$/, "");
for (const f of files) {
  try {
    const mod = await import(pathToFileURL(path.resolve(inDir, f)).href);
    const fn = Object.entries(mod).find(([k]) => k.startsWith("setup_"))?.[1];
    const shape = fn(oc);
    if (shape.IsNull()) throw new Error("empty shape");
    if (!new oc.BRepCheck_Analyzer(shape, true, false).IsValid_2()) warnings.push(f_name(f));
    if (single) builder.Add(assembly, shape);
    else writeStep(shape, path.join(outDir, f.replace(/\.js$/, ".step")));
    ok++;
  } catch (e) {
    failed.push(`${f}: ${e.message ?? e}`);
  }
}
if (single) writeStep(assembly, path.join(outDir, single));
console.log(`${ok}/${files.length} exported to ${outDir}`);
for (const m of failed) console.error("FAILED " + m);
if (warnings.length) console.error(`WARNING ${warnings.length} shape(s) fail BRepCheck: ${warnings.join(", ")}`);
process.exit(failed.length ? 1 : 0);
