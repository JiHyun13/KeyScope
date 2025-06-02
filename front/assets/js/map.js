// 📍 전체 키워드 시각화 및 요약 팝업 기능 포함된 마인드맵 JS

const svg = document.getElementById("mindmap");
const backBtn = document.getElementById("backBtn");
const output = document.getElementById("output");
let currentCenter = "";

const params = new URLSearchParams(window.location.search);
const initialKeyword = params.get("query") || "골프";
const expandedData = {};

function startExpandCrawlingAndRender(keyword) {
  if (output) {
    output.innerText = "로딩 중...";
    output.classList.add("loading-text");
  }

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

      const data = json.expanded_keywords || {};
      for (const key in data) {
        const node = data[key];
        expandedData[key] = {};
        if (key === keyword) {
          expandedData[key].primary = node.children ? node.children.map(child => ({
            name: child.name,
            score: child.score
          })) : [];
        } else {
          expandedData[key].secondary = node.children ? node.children.map(child => ({
            name: child.name,
            score: child.score
          })) : [];
        }
      }

      renderMap(keyword, expandedData);

      if (output) {
        output.classList.remove("loading-text");
        output.innerText = "로드 완료";
      }
    })
    .catch(err => {
      console.error("서버 요청 실패:", err);
    });
}

startExpandCrawlingAndRender(initialKeyword);

function renderMap(center, data) {
  svg.innerHTML = "";
  currentCenter = center;

  const cx = window.innerWidth / 2;
  const cy = window.innerHeight / 2;
  const centerR = 30;

  drawCircle(cx, cy, centerR, "center", center);

  const primaries = data[center]?.primary || [];
  const rPrimaryBase = 60;
  const radius1 = 220;
  const angleStep1 = 360 / (primaries.length || 1);

  if (primaries.length > 0) {
    primaries.forEach((label, i) => {
      const childScore = label.score || 1;
      const rPrimary = rPrimaryBase * childScore;
      const angle = (angleStep1 * i - 90) * Math.PI / 180;
      const x = cx + radius1 * Math.cos(angle);
      const y = cy + radius1 * Math.sin(angle);
      drawLine(cx, cy, x, y, "gray");
      drawCircle(x, y, rPrimary, "primary", label.name, label.score, () => {
        renderMap(label.name, data);
      });

      const secondaryList = data[label.name]?.secondary || [];
      const rSecondaryBase = 45;
      const angleStep2 = 60;
      const offsetStart = -((secondaryList.length) * angleStep2) / 2;

      secondaryList.forEach((sLabel, j) => {
        const jitter = (Math.random() - 0.5) * 20;
        const offsetAngle = (offsetStart + j * angleStep2 + jitter) * Math.PI / 180;
        const sx = x + 140 * Math.cos(offsetAngle);
        const sy = y + 140 * Math.sin(offsetAngle);

        const grandchildScore = sLabel.score || 1;
        const rSecondary = rSecondaryBase * grandchildScore;

        drawLine(x, y, sx, sy, "lightgray");
        drawCircle(sx, sy, rSecondary, "secondary", sLabel.name, sLabel.score, () => {
          showPopup(sLabel.name);
        });
      });
    });
  } else {
    const secondaryList = data[center]?.secondary || [];
    const rSecondaryBase = 45;
    const angleStep2 = 360 / secondaryList.length;

    secondaryList.forEach((sLabel, i) => {
      const offsetAngle = (angleStep2 * i - 90) * Math.PI / 180;
      const sx = cx + radius1 * Math.cos(offsetAngle);
      const sy = cy + radius1 * Math.sin(offsetAngle);

      const grandchildScore = sLabel.score || 1;
      const rSecondary = rSecondaryBase * grandchildScore;

      drawLine(cx, cy, sx, sy, "lightgray");
      drawCircle(sx, sy, rSecondary, "secondary", sLabel.name, sLabel.score, () => {
        showPopup(sLabel.name);
      });
    });
  }

  backBtn.style.display = currentCenter !== initialKeyword ? "block" : "none";
}

function drawCircle(x, y, r, type, label, score, onClick) {
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
  startExpandCrawlingAndRender(initialKeyword);
});

async function showPopup(keyword) {
  const existing = document.getElementById("popup-box");
  if (existing) existing.remove();

  const popup = document.createElement("div");
  popup.id = "popup-box";
  popup.className = "article-box";
  popup.innerHTML = `
    <span class="close" onclick="this.parentElement.remove()" style="position:absolute; top:10px; right:15px; cursor:pointer; font-size:18px;">✖</span>
    <h2>📌 "${keyword}" 관련 기사</h2>
    <div id="article-list" style="margin-top: 10px;"></div>
    <div id="summary-box" style="margin-top:20px; padding:10px; border-top:1px solid #ccc;"></div>
  `;
  document.body.appendChild(popup);

  const list = document.getElementById("article-list");
  list.innerHTML = "";

  try {
    const res = await fetch(`http://localhost:5000/api/articles?keyword=${encodeURIComponent(keyword)}`);
    const result = await res.json();

    if (!result.articles || result.articles.length === 0) {
      list.innerHTML = "<p>관련 기사가 없습니다.</p>";
      return;
    }

    result.articles.forEach((article, idx) => {
      const p = document.createElement("p");
      p.textContent = `${idx + 1}. ${article.title}`;
      p.style.cursor = "pointer";
      p.style.margin = "6px 0";
      p.style.color = "#007bff";
      p.style.textDecoration = "underline";

      p.addEventListener("click", async () => {
        const summaryBox = document.getElementById("summary-box");
        summaryBox.innerHTML = "🔄 기사 요약 중...";

        try {
          const contentRes = await fetch(`http://localhost:5000/api/article_content?article_id=${article.id}`);
          const contentData = await contentRes.json();

          console.log("📄 가져온 기사 contentData:", contentData);

          if (!contentData || contentData.error || !contentData.content || contentData.content.trim() === "") {
            console.warn("⚠️ 본문 없음 또는 에러 응답:", contentData);
            summaryBox.innerHTML = "❌ 기사 본문이 비어 있거나 가져오지 못했습니다.";
            return;
          }
          console.log("📋 contentData.content 타입:", typeof contentData.content);
          console.log("📋 contentData.content 값:", contentData.content);


          const summaryRes = await fetch("http://localhost:5000/summarize", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: contentData.content })
            
          });

          const summaryData = await summaryRes.json();
          console.log("🧠 요약 결과:", JSON.stringify(summaryData, null, 2));

          const summaryRaw = summaryData.summary;
          let summaryText;
          if (typeof summaryRaw === "string") {
            summaryText = summaryRaw;
          } else if (summaryRaw?.error) {
            summaryText = `❌ 요약 실패: ${summaryRaw.error}`;
          } else {
            summaryText = "요약 결과 없음";
          }

          summaryBox.innerHTML = `
            <h3>📰 ${article.title}</h3>
            <p>${summaryText}</p>
            <a href="${article.url}" target="_blank" class="view-link">원본 기사 보기</a>
          `;
        } catch (err) {
          console.error("❌ 요약 중 에러 발생:", err);
          summaryBox.innerHTML = "❌ 기사 요약에 실패했습니다.";
        }
      });

      list.appendChild(p);
    });
  } catch (err) {
    console.error("❌ 기사 불러오기 실패:", err);
    list.innerHTML = "<p>❌ 기사 목록을 불러오지 못했습니다.</p>";
  }
}
