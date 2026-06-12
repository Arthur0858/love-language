#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const __filename = fileURLToPath(import.meta.url);
const ROOT = path.resolve(path.dirname(__filename), "..");
const PROMOTION_DIR = path.join(ROOT, "docs", "promotion", "first-round");
const TRACKER_CSV = path.join(PROMOTION_DIR, "kpi-tracker.csv");
const PROFILE_TRACKER_CSV = path.join(PROMOTION_DIR, "platform-profile-tracker.csv");
const LEAD_INTAKE_CSV = path.join(PROMOTION_DIR, "lead-intake-tracker.csv");
const NEXT_ACTIONS_JSON = path.join(PROMOTION_DIR, "next-actions.json");
const WEEKLY_SUMMARY_JSON = path.join(PROMOTION_DIR, "weekly-summary.json");
const WEEK_EXECUTION_JSON = path.join(PROMOTION_DIR, "week-1-execution-sheet.json");
const OUTPUT_XLSX = path.join(PROMOTION_DIR, "lovetypes-first-round-kpi-workbook.xlsx");

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];
    if (quoted) {
      if (char === '"' && next === '"') {
        field += '"';
        index += 1;
      } else if (char === '"') {
        quoted = false;
      } else {
        field += char;
      }
    } else if (char === '"') {
      quoted = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n") {
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else if (char !== "\r") {
      field += char;
    }
  }
  if (field || row.length) {
    row.push(field);
    rows.push(row);
  }
  return rows;
}

function valuesForObjects(objects, headers) {
  return [headers, ...objects.map((item) => headers.map((header) => item?.[header] ?? ""))];
}

function executionRows(sheet) {
  const rows = [];
  for (const script of sheet.scripts ?? []) {
    for (const platform of script.platforms ?? []) {
      rows.push({
        week: sheet.week,
        taskId: script.taskId,
        scriptId: script.scriptId,
        guardianId: script.guardianId,
        guardianName: script.guardianName,
        contentAngle: script.contentAngle,
        title: script.title,
        platform: platform.platform,
        label: platform.label,
        scheduledDate: platform.scheduledDate,
        scheduledTime: platform.scheduledTime,
        timezone: platform.timezone,
        trackedUrl: platform.trackedUrl,
        caption: platform.caption,
        writeback: (platform.writeback ?? []).join(", "),
      });
    }
  }
  return rows;
}

function profileGateRows(sheet) {
  return (sheet.profileGates ?? []).map((gate) => ({
    platform: gate.platform,
    label: gate.label,
    ready: gate.ready ? "YES" : "NO",
    status: gate.status,
    profileLinkLabel: gate.profileLinkLabel,
    profileLink: gate.profileLink,
    bio: gate.bio,
    pinnedComment: gate.pinnedComment,
    writeback: (gate.writeback ?? []).join(", "),
  }));
}

function writeMatrix(sheet, startCell, matrix) {
  if (!matrix.length || !matrix[0].length) return;
  const width = Math.max(...matrix.map((row) => row.length));
  const normalized = matrix.map((row) => [...row, ...Array(width - row.length).fill("")]);
  const start = startCell.match(/^([A-Z]+)(\d+)$/);
  if (!start) throw new Error(`Invalid start cell: ${startCell}`);
  const startCol = columnToNumber(start[1]);
  const startRow = Number(start[2]);
  const endRow = startRow + normalized.length - 1;
  const endCol = startCol + width - 1;
  sheet.getRange(`${startCell}:${numberToColumn(endCol)}${endRow}`).values = normalized;
}

function columnToNumber(col) {
  return col.split("").reduce((value, char) => value * 26 + char.charCodeAt(0) - 64, 0);
}

function numberToColumn(num) {
  let col = "";
  let value = num;
  while (value > 0) {
    const mod = (value - 1) % 26;
    col = String.fromCharCode(65 + mod) + col;
    value = Math.floor((value - mod) / 26);
  }
  return col;
}

async function main() {
  const trackerRows = parseCsv(await fs.readFile(TRACKER_CSV, "utf8"));
  const profileTrackerRows = parseCsv(await fs.readFile(PROFILE_TRACKER_CSV, "utf8"));
  const leadIntakeRows = parseCsv(await fs.readFile(LEAD_INTAKE_CSV, "utf8"));
  const nextActions = JSON.parse(await fs.readFile(NEXT_ACTIONS_JSON, "utf8"));
  const weeklySummary = JSON.parse(await fs.readFile(WEEKLY_SUMMARY_JSON, "utf8"));
  const weekExecution = JSON.parse(await fs.readFile(WEEK_EXECUTION_JSON, "utf8"));
  const headers = trackerRows[0] ?? [];
  const workbook = Workbook.create();
  const dashboard = workbook.worksheets.add("Dashboard");
  const tracker = workbook.worksheets.add("KPI Tracker");
  const profileTracker = workbook.worksheets.add("Platform Profiles");
  const leadIntake = workbook.worksheets.add("Lead Intake");
  const weekExecutionSheet = workbook.worksheets.add("Week 1 Execution");
  const actions = workbook.worksheets.add("Next Actions");
  const dictionary = workbook.worksheets.add("Data Dictionary");

  writeMatrix(dashboard, "A1", [
    ["LoveTypes First Round KPI Workbook"],
    ["Generated", weeklySummary.generatedAt],
    ["Tracker rows with activity", weeklySummary.trackerRows],
    ["Tracker rows total", weeklySummary.trackerTotalRows],
    ["Platform profile rows with activity", weeklySummary.profileTrackerRows],
    ["Platform profile rows total", weeklySummary.profileTrackerTotalRows],
    ["Lead intake template rows", Math.max(leadIntakeRows.length - 1, 0)],
    ["Week 1 profile gates pending", weekExecution.profilePendingCount],
    ["Week 1 platform posts", weekExecution.platformPostCount],
    ["Empty data safety mode", nextActions.dataState.emptyDataMode ? "YES" : "NO"],
    [""],
    ["Metric", "Value"],
    ["Views", weeklySummary.totals.views],
    ["Site clicks", weeklySummary.totals.site_clicks],
    ["Quiz starts", weeklySummary.totals.quiz_starts],
    ["Quiz completions", weeklySummary.totals.quiz_completions],
    ["Route interest", weeklySummary.computedTotals.routeInterest],
    ["Revenue intent", weeklySummary.computedTotals.revenueIntent],
    ["Lead intent", weeklySummary.computedTotals.leadIntent],
    [""],
    ["Recommended actions"],
    ...nextActions.actions.map((action) => [action.priority, action.summary]),
  ]);

  writeMatrix(tracker, "A1", trackerRows);
  writeMatrix(profileTracker, "A1", profileTrackerRows);
  writeMatrix(leadIntake, "A1", leadIntakeRows);

  const profileGateHeaders = ["platform", "label", "ready", "status", "profileLinkLabel", "profileLink", "bio", "pinnedComment", "writeback"];
  const executionHeaders = [
    "week",
    "taskId",
    "scriptId",
    "guardianId",
    "guardianName",
    "contentAngle",
    "title",
    "platform",
    "label",
    "scheduledDate",
    "scheduledTime",
    "timezone",
    "trackedUrl",
    "caption",
    "writeback",
  ];
  writeMatrix(weekExecutionSheet, "A1", [
    ["Week 1 Profile Gates"],
    ...valuesForObjects(profileGateRows(weekExecution), profileGateHeaders),
    [""],
    ["Week 1 Platform Posts"],
    ...valuesForObjects(executionRows(weekExecution), executionHeaders),
  ]);

  const actionHeaders = [
    "taskId",
    "week",
    "slot",
    "guardianId",
    "guardianName",
    "contentAngle",
    "title",
    "trackedUrl",
    "primaryFreeItemId",
    "ownedLeadItemId",
    "supplyRoute",
    "lunaScene",
    "keepsake",
  ];
  writeMatrix(actions, "A1", valuesForObjects(nextActions.selectedTasks, actionHeaders));

  writeMatrix(dictionary, "A1", [
    ["Field", "Meaning"],
    ["site_clicks", "Clicks from social profile/caption into LoveTypes."],
    ["quiz_starts", "Sessions where the 15-question guardian quiz begins."],
    ["quiz_completions", "Completed quiz sessions; primary first-round KPI."],
    ["profile_clicks", "Clicks on social Bio/Profile links before visitors reach LoveTypes."],
    ["profile_link_set_date", "Date the platform Bio/Profile tracked link was set live."],
    ["free_keepsake_downloads", "Guardian identity asset save or print intent."],
    ["supply_lead_requests", "Owned email/request demand for guardian supply assets."],
    ["luna_pack_clicks", "Luna Gumroad product exploration."],
    ["affiliate_book_clicks", "Affiliate book route exploration."],
    ["contact_requests", "High-intent contact or path-summary mailto request."],
    ["lead-intake-tracker.csv", "Template rows for real Contact, waitlist, Luna, or repair supply requests. Template rows are not user data."],
  ]);

  await fs.mkdir(PROMOTION_DIR, { recursive: true });
  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(OUTPUT_XLSX);

  const errors = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 100 },
    summary: "formula error scan",
  });
  let renderedSheets = 0;
  const sheetNames = ["Dashboard", "KPI Tracker", "Platform Profiles", "Lead Intake", "Week 1 Execution", "Next Actions", "Data Dictionary"];
  for (const sheetName of sheetNames) {
    const range = sheetName === "Week 1 Execution" ? "A1:O28" : sheetName === "Lead Intake" ? "A1:Q18" : "A1:H24";
    await workbook.render({ sheetName, range, scale: 1 });
    renderedSheets += 1;
  }
  console.log(errors.ndjson);
  console.log(`promotion_spreadsheet=${OUTPUT_XLSX}`);
  console.log(`promotion_spreadsheet_sheets=${sheetNames.length}`);
  console.log(`promotion_spreadsheet_rendered_sheets=${renderedSheets}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
