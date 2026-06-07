document.addEventListener('click', function(e) {
    if (!e.target.classList.contains('description-generate-btn')) return;
    var d = e.target.parentElement.querySelector('textarea');
    if (!d) return;
    if (d.value) { e.target.textContent = 'Already has text'; return; }
    var s = document.getElementById('id_subject');
    var y = document.getElementById('id_year');
    var ex = document.getElementById('id_exam');
    var sj = s ? s.value : '';
    var yr = y ? y.value : '';
    var examEl = ex ? ex.options[ex.selectedIndex] : null;
    var examName = examEl ? examEl.text : '';
    var tmpl = [
        'Looking for ' + examName + ' ' + yr + ' ' + sj + ' question paper? Download the official PYQ PDF for free. Ideal for practicing and understanding the exam pattern before the actual test.',
        'Download ' + examName + ' ' + yr + ' ' + sj + ' previous year question paper PDF. Practice with real exam questions to boost your preparation and score higher.',
        'Free ' + examName + ' ' + yr + ' ' + sj + ' question paper PDF download. Practice ' + sj + ' questions from the actual ' + examName + ' exam to improve your performance.',
        'Prepare for ' + examName + ' with the official ' + yr + ' ' + sj + ' question paper. Download the PDF and practice from the real exam. Completely free.',
        'Get the ' + examName + ' ' + yr + ' ' + sj + ' PYQ PDF for free. Solve actual exam questions and build confidence for your upcoming ' + examName + ' test.',
    ];
    var idx = Math.abs((examName + sj + yr).split('').reduce(function(a, c) { return a + c.charCodeAt(0); }, 0)) % tmpl.length;
    d.value = tmpl[idx];
    e.target.textContent = 'Done!';
});
