// 요소 선택
const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");
const output = document.getElementById("output");

// 버튼 클릭 이벤트
searchBtn.addEventListener("click", () => {
  const keyword = searchInput.value.trim();

  if (!keyword) {
    alert("검색어를 입력해주세요!");
    return;
  }

  // ✅ 로딩 메시지 표시
  if (output) {
    output.classList.add("loading-text");
    output.innerText = ""; // 텍스트는 CSS 애니메이션에서 처리
  }

  // ✅ 기사 수집 요청
  fetch("http://localhost:5000/crawl", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: keyword })
  })
    .then(response => response.json())
    .then(data => {
      console.log("✅ 기사 수집 결과:", data);

      if (output) {
        output.classList.remove("loading-text");
        output.innerText = data.message || `❌ 오류: ${data.error}`;
      }

      // ✅ 결과 페이지로 이동
      window.location.href = `map.html?query=${encodeURIComponent(keyword)}`;
    })
    .catch(err => {
      console.error("❌ 서버 요청 실패:", err);
      if (output) {
        output.classList.remove("loading-text");
        output.innerText = `❌ 서버 요청 실패: ${err}`;
      }
    });
});

// Enter 키 처리
searchInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    searchBtn.click();
  }
});
