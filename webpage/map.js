const svg = document.getElementById("mindmap");
const backBtn = document.getElementById("backBtn");
const historyStack = [];

const params = new URLSearchParams(window.location.search);
const initialKeyword = params.get("query") || "중심";

const data = {
  "중심": {
    primary: ["1차-A", "1차-B", "1차-C"]
  },
  "1차-A": {
    secondary: ["2차 A-1", "2차 A-2"]
  },
  "1차-B": {
    secondary: ["2차 B-1", "2차 B-2"]
  },
  "1차-C": {
    secondary: ["2차 C-1", "2차 C-2", "2차 C-3"]
  }
};

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

  if (secondaries.length > 0) {
    const angleStep = 360 / secondaries.length;
    secondaries.forEach((label, i) => {
      const angle = (angleStep * i - 90) * Math.PI / 180;
      const x = cx + 220 * Math.cos(angle);
      const y = cy + 220 * Math.sin(angle);
      drawLine(cx, cy, x, y, "lightgray");
      drawCircle(x, y, rSecondary, "secondary", label, () => {
        showPopup(label);
      });
    });
  }

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
    <span class="close" onclick="this.parentElement.remove()" style="position:absolute; top:10px; right:15px; cursor:pointer; font-size:18px;">✖</span>
    <h2>📌 "${keyword}" 관련 기사</h2>
    <ul id="article-list"><li>불러오는 중...</li></ul>
  `;
  document.body.appendChild(popup);

  // ✅ 실제 API 연동 (API 주소 변경 필요)
  fetch(`https://api.example.com/articles?keyword=${encodeURIComponent(keyword)}`)
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById("article-list");
      list.innerHTML = "";
      data.articles.forEach((article, idx) => {
        const li = document.createElement("li");
        li.innerHTML = `<input type="checkbox" id="a${idx}"><label for="a${idx}"> ${idx + 1}. ${article.title}</label>`;
        list.appendChild(li);
      });
    })
    .catch(() => {
      document.getElementById("article-list").innerHTML = "<li>기사 불러오기 실패</li>";
    });
}

if (!data[initialKeyword]) {
  data[initialKeyword] = { primary: ["1차-A", "1차-B", "1차-C"] };
}

renderMap(initialKeyword);
