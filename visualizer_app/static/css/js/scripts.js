document.addEventListener('DOMContentLoaded', function () {
  const columnX = document.getElementById('column_x');
  const columnY = document.getElementById('column_y');

  columnX.addEventListener('change', function () {
      const selectedX = columnX.value;
      Array.from(columnY.options).forEach(option => {
          option.disabled = option.value === selectedX;
      });
  });

  columnY.addEventListener('change', function () {
      const selectedY = columnY.value;
      Array.from(columnX.options).forEach(option => {
          option.disabled = option.value === selectedY;
      });
  });
});
