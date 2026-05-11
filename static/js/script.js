document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('input[type="number"]').forEach((input) => {
    input.addEventListener("input", () => {
      const min = Number(input.min);
      const max = Number(input.max);
      const value = Number(input.value);

      if (input.value === "") {
        return;
      }

      if (!Number.isNaN(min) && value < min) {
        input.value = input.min;
      }

      if (input.max && !Number.isNaN(max) && value > max) {
        input.value = input.max;
      }
    });
  });
});
