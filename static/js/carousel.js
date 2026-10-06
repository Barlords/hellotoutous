(function () {
  var root = document.querySelector("[data-carousel]");
  if (!root) {
    return;
  }
  var slides = Array.prototype.slice.call(root.querySelectorAll("[data-slide]"));
  var bar = root.querySelector("[data-carousel-progress] span");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var index = 0;
  var timer = null;
  var duration = 4000;

  function show(next) {
    index = (next + slides.length) % slides.length;
    slides.forEach(function (slide, slideIndex) {
      slide.hidden = slideIndex !== index;
    });
  }

  function restartProgress() {
    if (!bar || reduce) {
      return;
    }
    bar.style.animation = "none";
    void bar.offsetWidth;
    bar.style.animation = "carousel-remaining " + duration + "ms linear forwards";
  }

  function isPaused() {
    return reduce || root.matches(":hover") || root.contains(document.activeElement);
  }

  function stop() {
    if (timer !== null) {
      window.clearInterval(timer);
      timer = null;
    }
    if (bar) {
      bar.style.animationPlayState = "paused";
    }
  }

  function play() {
    if (timer !== null) {
      window.clearInterval(timer);
      timer = null;
    }
    if (isPaused()) {
      if (bar) {
        bar.style.animationPlayState = "paused";
      }
      return;
    }
    restartProgress();
    timer = window.setInterval(function () {
      show(index + 1);
      restartProgress();
    }, duration);
  }

  root.addEventListener("mouseenter", stop);
  root.addEventListener("mouseleave", play);
  root.addEventListener("focusin", stop);
  root.addEventListener("focusout", play);
  root.querySelector("[data-carousel-prev]").addEventListener("click", function () {
    show(index - 1);
    restartProgress();
    play();
  });
  root.querySelector("[data-carousel-next]").addEventListener("click", function () {
    show(index + 1);
    restartProgress();
    play();
  });
  show(0);
  play();
})();
