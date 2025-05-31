const svg = document.getElementById("mindmap");
const backBtn = document.getElementById("backBtn");
const historyStack = [];

const params = new URLSearchParams(window.location.search);
const initialKeyword = params.get("query") || "중심";

// ✅ 트리 데이터 파싱 및 변환
const rawTree = sessionStorage.getItem("treeData");
const treeData = rawTree ? JSON.parse(rawTree) : null;
const data = treeData ? convertTreeToMap(treeData) : {};

function convertTreeToMap(treeNode) {
  const map = {};

  function traverse(node) {
    if (!node.children) return;

    const childrenNames = node.children.map(child => child.name);
    map[node.name] = { primary: childrenNames };

    node.children.forEach(child => {
      if (child.children && child.children.length > 0) {
        map[child.name] = { secondary: child.children.map(c => c.name) };
        traverse(child);
      }
    });
  }

  traverse(treeNode);
  return map;
}

function renderMap(center) {
  svg.innerHTML = "";
  const cx = window.innerWidth / 2;
  const cy = window.innerHeight / 2;
  const centerR = 30;
  drawCircle(cx, cy, centerR, "center", center);

  const primaries = data[center]?.primary || [];
  const secondaries = data[center]?.secondary || [];

  const rPrimary = 60, rSecondary = 45;
  const radius1 = 220;
  const angleStep1 = 360 / primaries.length;

  primaries.forEach((label, i) => {
    const angle = (angleStep1 * i - 90) * Math.PI / 180;
    const x = cx + radius1 * Math.cos(angle);
    const y = cy + radius1 * Math.sin(angle);
    drawLine(cx, cy, x, y, "gray");
    drawCircle(x, y, rPrimary, "primary", label, () => {
      historyStack.push(center);
      renderMap(label);
    });

    const secondaryList = data[label]?.secondary || [];
    const angleStep2 = 60;
    const offsetStart = -((secondaryList.length - 1) * angleStep2) / 2;

    secondaryList.forEach((sLabel, j) => {
      const offsetAngle = (offsetStart + j * angleStep2) * Math.PI / 180;
      const sx = x + 140 * Math.cos(offsetAngle);
      const sy = y + 140 * Math.sin(offsetAngle);
      drawLine(x, y, sx, sy, "lightgray");
      drawCircle(sx, sy, rSecondary, "secondary", sLabel, () => {
        showPopup(sLabel);
      });
    });
  });

  secondaries.forEach((label, i) => {
    const angle = (360 / secondaries.length * i - 90) * Math.PI / 180;
    const x = cx + 220 * Math.cos(angle);
    const y = cy + 220 * Math.sin(angle);
    drawLine(cx, cy, x, y, "lightgray");
    drawCircle(x, y, rSecondary, "secondary", label, () => {
      showPopup(label);
    });
  });

  backBtn.style.display = historyStack.length > 0 ? "block" : "none";
}

function drawCircle(x, y, r, type, label, onClick) {
  const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  circle.setAttribute("cx", x);
  circle.setAttribute("cy", y);
  circle.setAttribute("r", r);
  circle.setAttribute("class", type);
  if (onClick) circle.addEventListener("click", onClick);
  svg.appendChild(circle);

  const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
  text.setAttribute("x", x);
  text.setAttribute("y", y + 5);
  text.setAttribute("text-anchor", "middle");
  text.setAttribute("fill", type === "center" ? "white" : "black");
  text.textContent = label;
  svg.appendChild(text);
}

function drawLine(x1, y1, x2, y2, color) {
  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
  line.setAttribute("x1", x1);
  line.setAttribute("y1", y1);
  line.setAttribute("x2", x2);
  line.setAttribute("y2", y2);
  line.setAttribute("stroke", color);
  svg.insertBefore(line, svg.firstChild);
}

backBtn.addEventListener("click", () => {
  if (historyStack.length > 0) {
    const prev = historyStack.pop();
    renderMap(prev);
  }
});

function showPopup(keyword) {
  const existing = document.getElementById("popup-box");
  if (existing) existing.remove();

  const popup = document.createElement("div");
  popup.id = "popup-box";
  popup.className = "article-box";

  popup.innerHTML = `
    <span class="close" onclick="this.parentElement.remove()" style="position:absolute; top:10px; right:15px; cursor:pointer;">✖</span>
    <h2>📌 "\${keyword}" 관련 기사</h2>
    <div id="article-list"></div>
    <div id="summary-box" style="margin-top:20px; padding:10px; border-top:1px solid #ccc;"></div>
  `;

  document.body.appendChild(popup);

  const mockArticles = [
    {
      title: `${keyword} 관련 뉴스 1`,
      description: `${keyword}에 대한 기사 요약 내용입니다.`,
      link: "https://example.com/news1"
    },
    {
      title: `${keyword} 뉴스 속보`,
      description: `${keyword}에 대한 두 번째 기사입니다.`,
      link: "https://example.com/news2"
    }
  ];

  const list = document.getElementById("article-list");
  list.innerHTML = "";

  mockArticles.forEach((article, idx) => {
    const p = document.createElement("p");
    p.textContent = `${idx + 1}. \${article.title}`;
    p.style.cursor = "pointer";
    p.style.color = "#007bff";
    p.style.textDecoration = "underline";
    p.addEventListener("click", () => {
      document.getElementById("summary-box").innerHTML = `
        <h3>📰 \${article.title}</h3>
        <p>\${article.description}</p>
        <a href="\${article.link}" target="_blank">원본 기사 보기</a>
      `;
    });
    list.appendChild(p);
  });
}

renderMap(initialKeyword);
