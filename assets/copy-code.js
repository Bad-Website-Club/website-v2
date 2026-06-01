(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    let copySVG = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" stroke-width="1.75" fill="var(--bwc-purple)" stroke="none" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6.9998 6V3C6.9998 2.44772 7.44752 2 7.9998 2H19.9998C20.5521 2 20.9998 2.44772 20.9998 3V17C20.9998 17.5523 20.5521 18 19.9998 18H16.9998V20.9991C16.9998 21.5519 16.5499 22 15.993 22H4.00666C3.45059 22 3 21.5554 3 20.9991L3.0026 7.00087C3.0027 6.44811 3.45264 6 4.00942 6H6.9998ZM5.00242 8L5.00019 20H14.9998V8H5.00242ZM8.9998 6H16.9998V16H18.9998V4H8.9998V6Z"></path></svg>`;
    let copiedSVG = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--bwc-purple)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>`;

    let copyCodeBtns = document.querySelectorAll('.copy-code-btn');
    copyCodeBtns.forEach((copyCodeBtn) => {
      copyCodeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        let sibling = e.currentTarget.nextElementSibling;
        // Get only the (highlighted or non-highlighted) code blocks
        if (sibling.tagName !== 'DIV' && sibling.className !== 'highlight' && sibling.tagName !== 'PRE') {
          return;
        }
        let codeLines = [...sibling.firstChild.firstChild.children];
        let textResult = codeLines
          // Remove the line number
          .map(line => [...line.children].slice(1))
          .map(lineElements => lineElements.map(el => el.textContent))
          .join('');

          navigator.clipboard
          .writeText(textResult)
          .then(() => {
            copyCodeBtn.innerHTML = copiedSVG;
            setTimeout(() => (copyCodeBtn.innerHTML = copySVG), 1200);
          })
          .catch((err) => console.error('Copy failed:', err));
      });
    });
  });
})();
