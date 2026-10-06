(function () {
  var root = document.querySelector("[data-carousel]");
  if (!root) {
    return;
  }
  var slides = Array.prototype.slice.call(root.querySelectorAll("[data-slide]"));
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var index = 0;
  var timer = null;

  function show(next) {
    index = (next + slides.length) % slides.length;
    slides.forEach(function (slide, slideIndex) {
      slide.hidden = slideIndex !== index;
    });
  }

  function stop() {
    if (timer !== null) {
      window.clearInterval(timer);
      timer = null;
    }
  }

  function play() {
    var paused = reduce || root.matches(":hover") || root.contains(document.activeElement);
    stop();
    if (paused) {
      return;
    }
    timer = window.setInterval(function () {
      show(index + 1);
    }, 4000);
  }

  root.addEventListener("mouseenter", stop);
  root.addEventListener("mouseleave", play);
  root.addEventListener("focusin", stop);
  root.addEventListener("focusout", play);
  root.querySelector("[data-carousel-prev]").addEventListener("click", function () {
    show(index - 1);
  });
  root.querySelector("[data-carousel-next]").addEventListener("click", function () {
    show(index + 1);
  });
  show(0);
  play();
})();
