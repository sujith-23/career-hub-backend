from pathlib import Path
import re

path = Path(r"C:\New folder\career-hub-backend\frontend\index.html")

if not path.exists():
    raise SystemExit(f"ERROR: File not found: {path}")

html = path.read_text(encoding="utf-8")

start = html.find("function renderCourseComparison(){")
end = html.find("\nfunction renderEntranceExams(){", start)

if start == -1 or end == -1:
    raise SystemExit(
        "ERROR: Could not find renderCourseComparison()/renderEntranceExams() markers."
    )

new_function = r"""
function renderCourseComparison(){
  const main = document.getElementById('main');
  const crumb = document.getElementById('crumb');

  setCrumb(crumb, [{label:'Compare Courses', hash:'courses'}]);

  /*
   * Stream -> Course 1 -> Course 2
   * Course 1 and Course 2 are always taken from the
   * currently selected stream.
   */
  const coursesByStream = {};

  function collectCourses(streamId, stream, node, pathIds, breadcrumb){
    if(!node || typeof node !== 'object') return;

    const name =
      node.name ||
      pathIds[pathIds.length - 1] ||
      'Course';

    const trail = breadcrumb.concat(name);

    if(
      node.children &&
      typeof node.children === 'object' &&
      Object.keys(node.children).length > 0
    ){
      for(const [childId, child] of Object.entries(node.children)){
        collectCourses(
          streamId,
          stream,
          child,
          pathIds.concat(childId),
          trail
        );
      }
      return;
    }

    if(!coursesByStream[streamId]){
      coursesByStream[streamId] = {
        id: streamId,
        name: stream.name || streamId,
        courses: []
      };
    }

    coursesByStream[streamId].courses.push({
      id: `${streamId}/${pathIds.join('/')}`,
      name: name,
      stream: stream.name || streamId,
      streamId: streamId,
      breadcrumb: trail.slice(1).join(' → '),

      duration:
        node.duration ||
        node.courseDuration ||
        node.durationYears ||
        'Not specified',

      entrance:
        node.entrance ||
        'See current admission notification',

      focus:
        node.focus ||
        node.desc ||
        (
          Array.isArray(node.coreSubjects)
            ? node.coreSubjects.join(', ')
            : 'Not specified'
        ),

      careers:
        Array.isArray(node.jobRoles) && node.jobRoles.length
          ? node.jobRoles.join(', ')
          : 'Not specified',

      skills:
        Array.isArray(node.skills) && node.skills.length
          ? node.skills.join(', ')
          : 'Not specified',

      higherStudies:
        Array.isArray(node.higherStudies) && node.higherStudies.length
          ? node.higherStudies.join(', ')
          : 'Not specified'
    });
  }

  for(const [streamId, stream] of Object.entries(DATA || {})){
    if(!stream) continue;

    for(const [pathId, pathNode] of Object.entries(stream.paths || {})){
      collectCourses(
        streamId,
        stream,
        pathNode,
        [pathId],
        [stream.name || streamId]
      );
    }
  }

  const streamList = Object.values(coursesByStream);

  if(!streamList.length){
    main.innerHTML = `
      <a class="back-link" href="#/">‹ Back to home</a>
      <div class="page-head">
        <div class="code">CAREER TOOLS</div>
        <h1>Compare Courses</h1>
        <p>No courses are currently available.</p>
      </div>
    `;
    return;
  }

  const escapeHtml = value =>
    String(value ?? '')
      .replace(/&/g,'&amp;')
      .replace(/</g,'&lt;')
      .replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;')
      .replace(/'/g,'&#039;');

  main.innerHTML = `
    <a class="back-link" href="#/">‹ Back to home</a>

    <div class="page-head">
      <div class="code">CAREER TOOLS</div>
      <h1>Compare Courses</h1>
      <p>
        Select a stream first, then choose any two courses
        from that same stream.
      </p>
    </div>

    <div style="
      display:grid;
      grid-template-columns:repeat(3,minmax(0,1fr));
      gap:14px;
      margin-bottom:18px;
    ">

      <label style="
        font-size:0.82rem;
        font-weight:600;
      ">
        Stream

        <select id="compareStream" style="
          display:block;
          width:100%;
          margin-top:6px;
          padding:11px;
          border:1px solid var(--rail);
          border-radius:8px;
          background:var(--card);
          color:var(--ink);
          font:inherit;
        "></select>
      </label>

      <label style="
        font-size:0.82rem;
        font-weight:600;
      ">
        Course 1

        <select id="compareCourse1" style="
          display:block;
          width:100%;
          margin-top:6px;
          padding:11px;
          border:1px solid var(--rail);
          border-radius:8px;
          background:var(--card);
          color:var(--ink);
          font:inherit;
        "></select>
      </label>

      <label style="
        font-size:0.82rem;
        font-weight:600;
      ">
        Course 2

        <select id="compareCourse2" style="
          display:block;
          width:100%;
          margin-top:6px;
          padding:11px;
          border:1px solid var(--rail);
          border-radius:8px;
          background:var(--card);
          color:var(--ink);
          font:inherit;
        "></select>
      </label>

    </div>

    <div id="compareInfo" style="
      margin-bottom:18px;
      padding:12px 14px;
      background:var(--paper-deep);
      border:1px solid var(--rail);
      border-radius:8px;
      font-size:0.8rem;
      color:var(--ink-soft);
    "></div>

    <div id="comparisonTable"></div>
  `;

  const streamSelect = document.getElementById('compareStream');
  const course1Select = document.getElementById('compareCourse1');
  const course2Select = document.getElementById('compareCourse2');
  const compareInfo = document.getElementById('compareInfo');
  const comparisonTable = document.getElementById('comparisonTable');

  streamSelect.innerHTML = streamList.map((stream,index) => `
    <option value="${escapeHtml(stream.id)}" ${index === 0 ? 'selected' : ''}>
      ${escapeHtml(stream.name)}
    </option>
  `).join('');

  function getSelectedStream(){
    return coursesByStream[streamSelect.value] || {
      id: streamSelect.value,
      name: streamSelect.value,
      courses: []
    };
  }

  function populateCourses(){
    const selectedStream = getSelectedStream();
    const courses = selectedStream.courses || [];

    compareInfo.innerHTML = `
      <strong>${escapeHtml(selectedStream.name)}</strong>
      — ${courses.length} course/career path${courses.length === 1 ? '' : 's'} available.
      ${courses.length >= 2
        ? ' Choose any two courses from this stream.'
        : ' At least two courses are required for comparison.'}
    `;

    if(courses.length < 2){
      course1Select.innerHTML = courses.length
        ? `<option value="${escapeHtml(courses[0].id)}">${escapeHtml(courses[0].name)}</option>`
        : `<option value="">No courses available</option>`;

      course2Select.innerHTML =
        `<option value="">No second course available</option>`;

      course1Select.disabled = courses.length === 0;
      course2Select.disabled = true;
      comparisonTable.innerHTML = '';
      return;
    }

    course1Select.disabled = false;
    course2Select.disabled = false;

    course1Select.innerHTML = courses.map((course,index) => `
      <option value="${escapeHtml(course.id)}" ${index === 0 ? 'selected' : ''}>
        ${escapeHtml(course.name)}
      </option>
    `).join('');

    course2Select.innerHTML = courses.map((course,index) => `
      <option value="${escapeHtml(course.id)}" ${index === 1 ? 'selected' : ''}>
        ${escapeHtml(course.name)}
      </option>
    `).join('');

    renderComparison();
  }

  function renderComparison(){
    const selectedStream = getSelectedStream();
    const courses = selectedStream.courses || [];

    if(courses.length < 2){
      comparisonTable.innerHTML = '';
      return;
    }

    let c1 = courses.find(c => c.id === course1Select.value);
    let c2 = courses.find(c => c.id === course2Select.value);

    if(!c1) c1 = courses[0];
    if(!c2) c2 = courses[1];

    if(c1.id === c2.id){
      const replacement = courses.find(c => c.id !== c1.id);
      if(replacement){
        c2 = replacement;
        course2Select.value = replacement.id;
      }
    }

    const rows = [
      ['Stream', selectedStream.name, selectedStream.name],
      ['Course', c1.name, c2.name],
      ['Course path', c1.breadcrumb || 'Not specified', c2.breadcrumb || 'Not specified'],
      ['Duration', c1.duration, c2.duration],
      ['Entrance route', c1.entrance, c2.entrance],
      ['Main focus', c1.focus, c2.focus],
      ['Career options', c1.careers, c2.careers],
      ['Important skills', c1.skills, c2.skills],
      ['Higher studies', c1.higherStudies, c2.higherStudies]
    ];

    comparisonTable.innerHTML = `
      <div style="overflow-x:auto;">
        <table style="
          width:100%;
          border-collapse:collapse;
          background:var(--card);
          border:1px solid var(--rail);
          border-radius:8px;
          overflow:hidden;
        ">
          <thead>
            <tr>
              <th style="
                text-align:left;
                padding:13px;
                border-bottom:1px solid var(--rail);
                width:20%;
              ">Feature</th>

              <th style="
                text-align:left;
                padding:13px;
                border-bottom:1px solid var(--rail);
                border-left:1px solid var(--rail);
              ">${escapeHtml(c1.name)}</th>

              <th style="
                text-align:left;
                padding:13px;
                border-bottom:1px solid var(--rail);
                border-left:1px solid var(--rail);
              ">${escapeHtml(c2.name)}</th>
            </tr>
          </thead>

          <tbody>
            ${rows.map(row => `
              <tr>
                <td style="
                  padding:12px;
                  border-bottom:1px solid var(--rail);
                  font-weight:700;
                  vertical-align:top;
                ">${escapeHtml(row[0])}</td>

                <td style="
                  padding:12px;
                  border-bottom:1px solid var(--rail);
                  border-left:1px solid var(--rail);
                  vertical-align:top;
                ">${escapeHtml(row[1] || 'Not specified')}</td>

                <td style="
                  padding:12px;
                  border-bottom:1px solid var(--rail);
                  border-left:1px solid var(--rail);
                  vertical-align:top;
                ">${escapeHtml(row[2] || 'Not specified')}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>

      <p style="
        font-size:0.76rem;
        color:var(--ink-soft);
        margin-top:10px;
      ">
        Both courses belong to the selected stream.
        Verify current admission requirements before applying.
      </p>
    `;
  }

  streamSelect.addEventListener('change', populateCourses);
  course1Select.addEventListener('change', renderComparison);
  course2Select.addEventListener('change', renderComparison);

  populateCourses();
}
"""

html = html[:start] + new_function.strip() + html[end:]

# Safety checks: old UI must be gone from the function.
new_section = html[start:html.find("\nfunction renderEntranceExams(){", start)]
if "Course / Stream 1" in new_section or "Course / Stream 2" in new_section:
    raise SystemExit("ERROR: Old comparison labels are still present.")

if 'id="compareStream"' not in new_section:
    raise SystemExit("ERROR: compareStream was not inserted.")

# Backup the original before changing it.
backup = path.with_suffix(".index-backup.html")
backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
path.write_text(html, encoding="utf-8")

print("SUCCESS")
print(f"Updated: {path}")
print(f"Backup : {backup}")
print("")
print("Now run:")
print(r'findstr /N /I /C:"Course / Stream 1" frontend\index.html')
print("")
print("That command should print NOTHING.")
print("")
print(r'findstr /N /I /C:"compareStream" frontend\index.html')
print("")
print("That command should show the new compareStream code.")
