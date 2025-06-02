console.log("🚀 map.js 로드됨");

// 🔹 1. 초기 변수 설정
const svg = document.getElementById("mindmap");
const backBtn = document.getElementById("backBtn");
const output = document.getElementById("output"); // 로딩 메시지를 출력할 div
let currentCenter = "";  // 현재 중심이 되는 키워드 추적

// 쿼리 파라미터로 초기 키워드 받아오기
const params = new URLSearchParams(window.location.search);
const initialKeyword = params.get("query") || "골프"; // 기본 값으로 "골프"
const expandedData = {};
// 데이터를 서버로부터 가져오는 함수
function startExpandCrawlingAndRender(keyword) {
  // 로딩 메시지 표시
  if (output) {
    output.innerText = "로딩 중..."; // 로딩 메시지 표시
    output.classList.add("loading-text"); // CSS 애니메이션 추가
  }

<<<<<<< Updated upstream
  fetch("http://localhost:5000/expand", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: keyword }),
  })
    .then(res => res.json())
    .then(json => {
      if (json.error) {
        console.error("확장 크롤링 오류:", json.error);
        return;
      }
=======
let data = {}; // 키워드 그래프 데이터 객체

let alreadyInitialized = false;

let initialized = false;

async function initialize() {
  console.log("🧨 initialize() 실행됨");

  if (initialized) return; // ✅ 중복 방지
  initialized = true;

  try {
    console.log("🔥 초기화 시작");

    // 📰 기사 수집
    const crawlResponse = await fetch("http://localhost:5000/crawl", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: initialKeyword })
    });
    const crawlResult = await crawlResponse.json();
    if (!crawlResponse.ok) {
      console.error("❌ 수집 실패:", crawlResult.error);
      return;
    }

    // 🔗 키워드 그래프 요청
    const graphResponse = await fetch(`http://localhost:5000/api/keywords?query=${encodeURIComponent(initialKeyword)}`);
    const graphResult = await graphResponse.json();

    data = transformGraphToKeywordData(graphResult.graph, initialKeyword);
    renderMap(initialKeyword);

  } catch (err) {
    console.error("⚠️ 초기화 중 오류 발생:", err);
  }
}
>>>>>>> Stashed changes

      
      const data = json.expanded_keywords || {};
      
      // 데이터 변환
      for (const key in data) {
        const node = data[key];
        expandedData[key] = {};

        // 중심 키워드에 대한 primary
        if (key === keyword) {
          expandedData[key].primary = node.children ? node.children.map(child => ({
            name: child.name,
            score: child.score  // score 추가
          })) : [];
        } else {
          // 그 외 자식/손자에 대해서는 secondary만
          expandedData[key].secondary = node.children ? node.children.map(child => ({
            name: child.name,
            score: child.score  // score 추가
          })) : [];
        }
      }

      console.log("변환된 데이터:", JSON.stringify(expandedData, null, 2));

      // 맵을 그리기
      renderMap(keyword, expandedData);

      // 로딩 완료 후 메시지 업데이트
      if (output) {
        output.classList.remove("loading-text");
        output.innerText = "로드 완료"; // 완료 메시지로 변경
      }
    })
    .catch(err => {
      console.error("서버 요청 실패:", err);
    });
}

startExpandCrawlingAndRender(initialKeyword);

// 맵을 그리는 함수
function renderMap(center, data) {
  svg.innerHTML = ""; // 맵 초기화
  currentCenter = center;  // 현재 중심 키워드 저장

<<<<<<< Updated upstream
  const cx = window.innerWidth / 2;
  const cy = window.innerHeight / 2;
  const centerR = 30; // 중심 원 크기

  drawCircle(cx, cy, centerR, "center", center);  // 중심을 그리기

  const primaries = data[center]?.primary || []; // 자식 노드
  console.log("자식 노드:", primaries);
  const rPrimaryBase = 60; // 기본 자식 원 크기
=======
// 🔹 변환 함수: 백엔드 그래프(nodes/edges) → 기존 data 구조로
function transformGraphToKeywordData(graph, centerKeyword) {
  const result = {};
  result[centerKeyword] = { primary: [], secondary: [] };

  const levelMap = {};
  graph.nodes.forEach(n => {
    levelMap[n.id] = n.level;
  });

  graph.edges.forEach(edge => {
    const from = edge.from;
    const to = edge.to;

    if (from === centerKeyword) {
      result[centerKeyword].primary.push(to);
    } else {
      if (!result[from]) result[from] = { secondary: [] };
      if (!result[from].secondary.includes(to)) {
        result[from].secondary.push(to);
      }
    }
  });

  return result;
}

// 🔹 3. 마인드맵 시각화 함수
function renderMap(center) {
  svg.innerHTML = "";
  const cx = window.innerWidth / 2;
  const cy = window.innerHeight / 2;
  const centerR = 30;

  drawCircle(cx, cy, centerR, "center", center);
  const primaries = data[center]?.primary || [];
  const secondaries = data[center]?.secondary || [];

  const rPrimary = 60, rSecondary = 45;
>>>>>>> Stashed changes
  const radius1 = 220;
  const angleStep1 = 360 / (primaries.length || 1);  // 자식이 없으면 1로 나누어서 오류 방지

<<<<<<< Updated upstream
  // 자식 노드가 있을 때 그ㄴ리기
  if (primaries.length > 0) {
    primaries.forEach((label, i) => {
      const childScore = label.score || 1; // 자식의 score 값
      const rPrimary = rPrimaryBase * childScore; // score에 비례하여 크기 조정
=======
  // 1차 키워드
  primaries.forEach((label, i) => {
    const angle = (angleStep1 * i - 90) * Math.PI / 180;
    const x = cx + radius1 * Math.cos(angle);
    const y = cy + radius1 * Math.sin(angle);
    drawLine(cx, cy, x, y, "gray");
    drawCircle(x, y, rPrimary, "primary", label, () => {
      historyStack.push(center);
      renderMap(label);
    });
>>>>>>> Stashed changes

      const angle = (angleStep1 * i - 90) * Math.PI / 180;
      const x = cx + radius1 * Math.cos(angle);
      const y = cy + radius1 * Math.sin(angle);
      drawLine(cx, cy, x, y, "gray");
      drawCircle(x, y, rPrimary, "primary", label.name, label.score, () => {
        renderMap(label, data);  // 클릭한 자식을 새로운 중심으로 맵을 새로 그림
      });

<<<<<<< Updated upstream
      // 손자 노드가 있다면 그리기
      const secondaryList = data[label.name]?.secondary || [];
      console.log(label,"손자 노드:", secondaryList);
      const rSecondaryBase = 45;
      const angleStep2 = 60;
      const offsetStart = -((secondaryList.length ) * angleStep2) / 2;

      secondaryList.forEach((sLabel, j) => {
        const jitter = (Math.random() - 0.5) * 20;  // -10도 ~ +10도 범위로 흔들기
        const offsetAngle = (offsetStart + j * angleStep2 + jitter) * Math.PI / 180;
        const sx = x + 140 * Math.cos(offsetAngle);
        const sy = y + 140 * Math.sin(offsetAngle);

        const grandchildScore = sLabel.score || 1;  // 손자의 score 값
        const rSecondary = rSecondaryBase * grandchildScore; // score에 비례하여 크기 조정

        drawLine(x, y, sx, sy, "lightgray");
        drawCircle(sx, sy, rSecondary, "secondary", sLabel.name, sLabel.score, () => {
          showPopup(sLabel); // 손자 노드를 클릭하면 팝업 표시
        });
      });
=======
    secondaryList.forEach((sLabel, j) => {
      const offsetAngle = (offsetStart + j * angleStep2) * Math.PI / 180;
      const sx = x + 140 * Math.cos(offsetAngle);
      const sy = y + 140 * Math.sin(offsetAngle);
      drawLine(x, y, sx, sy, "lightgray");
      drawCircle(sx, sy, rSecondary, "secondary", sLabel, () => showPopup(sLabel));
>>>>>>> Stashed changes
    });
  } else {
    // 자식이 없을 때, secondary를 센터에 붙이기
    const secondaryList = data[center]?.secondary || [];
    const rSecondaryBase = 45;
    const angleStep2 = 360 / secondaryList.length;  // 전체 원주를 secondary 개수만큼 분할

<<<<<<< Updated upstream
    secondaryList.forEach((sLabel, i) => {
      const offsetAngle = (angleStep2 * i - 90) * Math.PI / 180;  // 각도를 분할하여 원형 배치
      const sx = cx + radius1 * Math.cos(offsetAngle);
      const sy = cy + radius1 * Math.sin(offsetAngle);

      const grandchildScore = sLabel.score || 1;  // 손자의 score 값
      const rSecondary = rSecondaryBase * grandchildScore; // score에 비례하여 크기 조정

      drawLine(cx, cy, sx, sy, "lightgray");
      drawCircle(sx, sy, rSecondary, "secondary", sLabel.name, sLabel.score, () => {
        showPopup(sLabel); // 손자 노드를 클릭하면 팝업 표시
      });
=======
  // 직접 붙은 2차 키워드
  if (secondaries.length > 0) {
    const angleStep = 360 / secondaries.length;
    secondaries.forEach((label, i) => {
      const angle = (angleStep * i - 90) * Math.PI / 180;
      const x = cx + 220 * Math.cos(angle);
      const y = cy + 220 * Math.sin(angle);
      drawLine(cx, cy, x, y, "lightgray");
      drawCircle(x, y, rSecondary, "secondary", label, () => showPopup(label));
>>>>>>> Stashed changes
    });
  }

  backBtn.style.display = currentCenter !== initialKeyword ? "block" : "none";  // 초기 키워드로 돌아가면 뒤로가기 버튼 숨기기
}

<<<<<<< Updated upstream
// 원 그리기
=======
// 🔹 4. 원 그리기
>>>>>>> Stashed changes
function drawCircle(x, y, r, type, label, onClick) {
  const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  circle.setAttribute("cx", x);
  circle.setAttribute("cy", y);
  circle.setAttribute("r", r);
  circle.setAttribute("class", type);
<<<<<<< Updated upstream
  if (onClick) circle.addEventListener("click", () => {
    if(type === "secondary") {
      showPopup(label);  // 손자 노드를 클릭하면 팝업 표시
      return;
    }
    else renderMap(label,expandedData);  
});
=======
  if (type === "center") circle.classList.add("center-animate");
  if (onClick) circle.addEventListener("click", onClick);
>>>>>>> Stashed changes
  svg.appendChild(circle);

  const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
  text.setAttribute("x", x);
  text.setAttribute("y", y + 5);
  text.setAttribute("text-anchor", "middle");
  text.setAttribute("fill", type === "center" ? "white" : "black");
  text.textContent = label;  // 표시할 텍스트에 score 추가
  svg.appendChild(text);
}

<<<<<<< Updated upstream
// 선 그리기
=======
// 🔹 5. 선 그리기
>>>>>>> Stashed changes
function drawLine(x1, y1, x2, y2, color) {
  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
  line.setAttribute("x1", x1);
  line.setAttribute("y1", y1);
  line.setAttribute("x2", x2);
  line.setAttribute("y2", y2);
  line.setAttribute("stroke", color);
  svg.insertBefore(line, svg.firstChild);
}

<<<<<<< Updated upstream
// 뒤로가기 버튼 클릭 이벤트
=======
// 🔹 6. 뒤로가기
>>>>>>> Stashed changes
backBtn.addEventListener("click", () => {
  startExpandCrawlingAndRender(initialKeyword);  // 기존 중심으로 돌아가기
});

<<<<<<< Updated upstream
// 팝업 표시 함수
=======
// 🔹 7. 팝업 기사 목록
>>>>>>> Stashed changes
function showPopup(keyword) {
  const existing = document.getElementById("popup-box");
  if (existing) existing.remove();

  const popup = document.createElement("div");
  popup.id = "popup-box";
  popup.className = "article-box";
<<<<<<< Updated upstream

  popup.innerHTML =  ` 
    <span class="close" onclick="this.parentElement.remove()" style="position:absolute; top:10px; right:15px; cursor:pointer; font-size:18px;">✖</span>
    <h2>📌 "${keyword}" 관련 기사</h2>
    <div id="article-list" style="margin-top: 10px;"></div>
    <div id="summary-box" style="margin-top:20px; padding:10px; border-top:1px solid #ccc;"></div>
  `;
  document.body.appendChild(popup);

  // 예시 기사 데이터
  const mockArticles = [
    {
      title: `${keyword} 관련 뉴스 1`,
      description: `${keyword}에 대한 기사 요약 내용입니다.`,
      link: "https://example.com/news1"
    },
    {
      title: `${keyword} 뉴스 속보`,
      description: `이것은 ${keyword}에 대한 두 번째 기사입니다.`,
      link: "https://example.com/news2"
    },
    {
      title: `${keyword} 분석 리포트`,
      description: `심층 분석된 ${keyword} 기사입니다.`,
      link: "https://example.com/news3"
    }
  ];

  const list = document.getElementById("article-list");
  list.innerHTML = "";

  mockArticles.forEach((article, idx) => {
    const p = document.createElement("p");
    p.textContent = `${idx + 1}. ${article.title}`;
    p.style.cursor = "pointer";
    p.style.margin = "6px 0";
    p.style.color = "#007bff";
    p.style.textDecoration = "underline";

    p.addEventListener("click", () => {
      document.getElementById("summary-box").innerHTML = `
        <h3>📰 ${article.title}</h3>
        <p>${article.description}</p>
        <a href="${article.link}" target="_blank" class="view-link">원본 기사 보기</a>
      `;
    });

    list.appendChild(p);
  });
}
=======
  popup.innerHTML = `
    <span class="close" id="popup-close" style="position:absolute; top:10px; right:15px; cursor:pointer; font-size:18px;">✖</span>
    <h2 id="popup-title">📌 "${keyword}" 관련 기사</h2>
    <ul id="article-list" style="margin-top:10px;"></ul>
  `;
  document.body.appendChild(popup);

  fetch(`http://localhost:5000/api/articles?keyword=${encodeURIComponent(keyword)}`)
    .then(response => response.json())
    .then(result => {
      const articles = result.articles || [];
      const list = document.getElementById("article-list");
      if (articles.length === 0) {
        const li = document.createElement("li");
        li.textContent = "관련 기사가 없습니다.";
        list.appendChild(li);
        return;
      }
      articles.forEach((article, idx) => {
        const li = document.createElement("li");
        li.textContent = `${idx + 1}. ${article.title}`;
        li.style.cursor = "pointer";
        li.onclick = () => renderArticleView(article, keyword);
        list.appendChild(li);
      });
    })
    .catch(error => {
      console.error("기사 불러오기 실패:", error);
      const li = document.createElement("li");
      li.textContent = "⚠️ 기사 불러오는 중 오류 발생";
      document.getElementById("article-list").appendChild(li);
    });

  document.getElementById("popup-close").onclick = () => popup.remove();
}

// 🔹 8. 기사 상세 보기 + 요약
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
    fetch("http://localhost:5000/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: article.body })
    })
      .then(response => response.json())
      .then(result => {
        document.getElementById("summaryResult").innerText = result.summary;
      })
      .catch(error => {
        console.error("요약 실패:", error);
        document.getElementById("summaryResult").innerText = "요약 중 오류 발생";
      });
  };

  document.getElementById("popup-back").onclick = () => showPopup(keyword);
}

// 🔹 9. 실행
document.addEventListener("DOMContentLoaded", () => {
  if (!initialized) {
    initialize();
  }
});s

>>>>>>> Stashed changes
