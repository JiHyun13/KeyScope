const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");
const output = document.getElementById("output");
const loadingWrapper = document.getElementById("loadingWrapper");

// ✅ 시작 시 확실히 숨기기 (혹시라도 안 숨겨진 경우 대비)
window.addEventListener("DOMContentLoaded", () => {
  loadingWrapper.style.display = "none";
});

searchBtn.addEventListener("click", () => {
  const keyword = searchInput.value.trim();

  if (!keyword) {
    alert("검색어를 입력해주세요!");
    return;
  }

  // ✅ 로딩 표시 시작
  output.innerText = "";
  loadingWrapper.style.display = "flex";

  fetch("http://localhost:5000/crawl", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: keyword })
  })
    .then(response => response.json())
    .then(data => {
      // ✅ 로딩 종료
      loadingWrapper.style.display = "none";

      if (data.message) {
        output.innerText = data.message;
      } else {
        output.innerText = `❌ 오류: ${data.error}`;
      }

      // ✅ 결과 페이지로 이동
      window.location.href = `map.html?query=${encodeURIComponent(keyword)}`;
    })
    .catch(err => {
      loadingWrapper.style.display = "none";
      output.innerText = `❌ 서버 요청 실패: ${err}`;
    });
});

searchInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    searchBtn.click();
  }
});

const darkToggle = document.getElementById("darkModeToggle");
darkToggle.addEventListener("change", () => {
  document.body.classList.toggle("dark-mode", darkToggle.checked);
});
