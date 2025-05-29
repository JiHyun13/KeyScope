const svg = document.getElementById("mindmap");
const backBtn = document.getElementById("backBtn");
const historyStack = [];

const params = new URLSearchParams(window.location.search);
const initialKeyword = params.get("query") || "중심";



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
  if (type === "center") {
  circle.classList.add("center-animate");
}

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
    <span class="close" id="popup-close" style="position:absolute; top:10px; right:15px; cursor:pointer; font-size:18px;">✖</span>
    <h2 id="popup-title">📌 "${keyword}" 관련 기사</h2>
    <ul id="article-list" style="margin-top:10px;"></ul>
  `;
  document.body.appendChild(popup);

  const mockArticles = [
    { id: "1", title: `"${keyword}"에 관한 첫 번째 기사입니다.`, body: "이것은 첫 번째 기사 내용입니다." },
    { id: "2", title: `"${keyword}" 관련 두 번째 기사`, body: "두 번째 기사 본문입니다." },
    { id: "3", title: `"${keyword}" 다룬 세 번째 뉴스`, body: "세 번째 뉴스 기사 내용." }
  ];

  const list = document.getElementById("article-list");
  mockArticles.forEach((article, idx) => {
    const li = document.createElement("li");
    li.textContent = `${idx + 1}. ${article.title}`;
    li.style.cursor = "pointer";
    li.onclick = () => renderArticleView(article, keyword); // ✨ 여기서 렌더 변경
    list.appendChild(li);
  });

  // X버튼은 닫기 역할
  document.getElementById("popup-close").onclick = () => popup.remove();
}

function renderArticleView(article, keyword) {
  const popup = document.getElementById("popup-box");
  popup.innerHTML = `
    <span class="close" id="popup-back" style="position:absolute; top:10px; right:15px; cursor:pointer; font-size:18px;">↩</span>
    <h2 id="popup-title">📌 ${article.title}</h2>
    <div id="articleContent" style="white-space:pre-wrap; margin-top:15px;">${article.body}</div>
    <div style="margin-top:15px;">
      <button id="summary-btn">요약 보기</button>
    </div>
    <div id="summaryResult" style="white-space:pre-wrap; margin-top:10px; font-style:italic;"></div>
  `;

  document.getElementById("summary-btn").onclick = () => {
    const summary = article.body.length > 100 ? article.body.slice(0, 100) + "..." : article.body;
    document.getElementById("summaryResult").innerText = summary;
  };

  // ⬅️ X를 뒤로가기 역할로
  document.getElementById("popup-back").onclick = () => showPopup(keyword);
}


//혜진, 요약 API호출 함수
function onArticleClick(article) {
  // 1. 팝업 타이틀을 기사 제목으로 변경
  const popupTitle = document.getElementById("popup-title");
  popupTitle.innerText = `📌 ${article.title}`;

  // 2. 기사 본문 표시
  const articleContent = document.getElementById("articleContent");
  articleContent.innerText = article.body;

  // 3. 요약 버튼 표시 및 이벤트 연결
  const summaryContainer = document.getElementById("summary-container");
  summaryContainer.style.display = "block";
  document.getElementById("summaryResult").innerText = "";

  const summaryBtn = document.getElementById("summary-btn");
  summaryBtn.onclick = () => {
    // 정적 요약 결과 - 테스트용
    const fakeSummary = article.body.length > 100
      ? article.body.substring(0, 100) + "..."
      : article.body;

    document.getElementById("summaryResult").innerText = fakeSummary;
  };
}




// 기존에 하드코딩된 data 사용 X
// 대신 API로부터 동적으로 불러오기
// 기존에 하드코딩된 data 사용 X
// 대신 API로부터 동적으로 불러오기
// let data = {};
// fetch("http://localhost:5000/api/keywords") ...

let data = {
  "이재명": { primary: ["대장동", "경기도"] },
  "대장동": { secondary: ["수사", "화천대유"] },
  "경기도": { secondary: ["지사직", "정책"] }
};

if (!data[initialKeyword]) {
  data[initialKeyword] = { primary: [] };
}
renderMap(initialKeyword);
