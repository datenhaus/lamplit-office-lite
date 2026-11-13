// =====================================================================
//  LAMPLIT OFFICE LITE – data file
//  This is the ONLY file you change. index.html stays as it is.
//  The page loads this file again every few seconds (see refreshSeconds).
//
//  Everything below is INVENTED SAMPLE DATA. Replace it with your own.
//  Plain JSON is fine too:  window.OFFICE = { "title": "...", ... };
//  Do not put passwords, API keys or private data in here:
//  everybody who can open the page can read this file.
// =====================================================================

// Demo helper: makes the sample look fresh at any time of day.
// In real use, write real times instead, e.g. "2030-01-15T14:05:00+01:00".
function minutesAgo(n) { return new Date(Date.now() - n * 60000).toISOString(); }

window.OFFICE = {
  title: "Harbor Lane Office",              // big film title
  kicker: "Night shift",                    // small line above the title (optional)
  subtitle: "Who is working on what, right now",   // line below the title (optional)
  goal: "Ship the spring newsletter by Friday.",
  updated: minutesAgo(0),                   // when this file was last written (ISO date and time)
  refreshSeconds: 30,                       // how often the page re-reads this file (5 to 3600)
  theme: "dark",                            // colours the page starts with: "dark", "light" or "auto" (follows the device).
                                            // A visitor can switch with the button or the T key; the browser remembers that choice.

  room: { title: "Workshop", note: "Where things get built" },

  // Up to six team members.
  // code      2 to 4 letters on the desk; also decides the look of the figure
  // desk      board | review | browser | terminal | chart | notes
  // status    working | waiting | done | review | blocked
  // progress  0 to 100
  // says      one sentence, shown like a film subtitle under the desk
  // started + minutes   optional: while status is "working" the bar then moves by itself
  team: [
    { code: "MO", name: "Morgan", role: "Lead: plans and signs off", desk: "board",
      status: "working", progress: 55, says: "Two tasks are in review. I am lining up tomorrow's work." },
    { code: "KA", name: "Kai", role: "Builder: writes the code", desk: "terminal",
      status: "working", started: minutesAgo(8), minutes: 20, says: "The sign-up form works. Now the thank-you page." },
    { code: "SA", name: "Sam", role: "Writer: newsletter copy", desk: "browser",
      status: "review", progress: 90, says: "Draft is with Jo. I am shortening the ending while I wait." },
    { code: "JO", name: "Jo", role: "Reviewer: honest feedback", desk: "review",
      status: "working", progress: 40, says: "Reading Sam's draft. Strong opening, the ending is too long." },
    { code: "RA", name: "Ravi", role: "Data: counts what happened", desk: "chart",
      status: "done", progress: 100, says: "Last week's numbers are in. Tuesday was the best day." },
    { code: "NO", name: "Noor", role: "QA: clicks through everything", desk: "notes",
      status: "blocked", progress: 30, says: "I need a test login for the sign-up page. I cannot go on without it." }
  ],

  // Small note at the bottom (optional)
  note: "Sample data. Every name and sentence on this page is invented to show the layout."
};
