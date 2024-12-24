$(document).ready(function() {
    let currentStep = 1;

    // Hàm xử lý cho nút "next"
    function nextStep() {
        if (currentStep < 3) {
            currentStep++;

            $.get(`/step/${currentStep}`, function(data) {
                $("#content-area").html(data);
            }).fail(function() {
                alert("Failed to load step. Please try again.");
            });
        } else {
            alert("You've completed the steps!");
        }
    }

    // Gán sự kiện cho tất cả các nút "next-btn", bao gồm cả những nút mới được thêm
    $(document).on("click", "button[name='next-btn']", function() {
        nextStep(); // Gọi hàm nextStep() khi nút được nhấn
    });
});

