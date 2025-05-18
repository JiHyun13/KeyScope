// 요소 선택
const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");

// 버튼 클릭 이벤트
searchBtn.addEventListener("click", function () {
  const keyword = searchInput.value.trim(); // 입력값 가져오기

  if (keyword) {
    alert(`'${keyword}' 를 검색합니다!`);
    // 여기에 실제 검색 동작을 추가할 수 있어
  } else {
    alert("검색어를 입력하세요.");
  }
});
