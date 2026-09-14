# PolicyGraph web app

The functional-alpha interface is a dependency-free HTML, CSS, and JavaScript client served by the FastAPI application on the same origin. It progressively discloses the committed sample graph by topic, relationship, evidence quote, policy status, and primary source.

Run `uvicorn policygraph.api:app --host 127.0.0.1 --port 8000` after an editable install and open <http://127.0.0.1:8000>. The UI requires JavaScript for exploration; API data remains available through `/docs` and `/api/graph`.

Accessibility provisions include semantic headings and landmarks, a skip link, native button controls, visible focus, live loading state, readable contrast, and explicit empty/error messages. Evidence is statically inline in cards. Automated checks cover structure; assistive-technology and moderated usability testing remain future work.

The UI intentionally labels the fixture corpus as synthetic, bounded, incomplete, and unsuitable for legal advice. It does not infer that missing sample data means missing real-world policy activity.

The UI labels each status as the source document's status on `status_as_of`, never as current law. Static assets resolve from a checkout or the relocatable wheel.
