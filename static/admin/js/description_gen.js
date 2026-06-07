document.querySelectorAll('.description-generate-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
        var d = this.parentElement.querySelector('textarea');
        if (d.value) { this.textContent = 'Already has text'; return; }
        var e = document.getElementById('id_exam');
        var s = document.getElementById('id_subject');
        var y = document.getElementById('id_year');
        var ex = e ? e.options[e.selectedIndex].text : '';
        var sj = s ? s.value : '';
        var yr = y ? y.value : '';
        var tmpl = [
            'Looking for ' + ex + ' ' + yr + ' ' + sj + ' question paper? Download the official PYQ PDF for free. Ideal for practicing and understanding the exam pattern before the actual test.',
            'Download ' + ex + ' ' + yr + ' ' + sj + ' previous year question paper PDF. Practice with real exam questions to boost your preparation and score higher.',
            'Free ' + ex + ' ' + yr + ' ' + sj + ' question paper PDF download. Practice ' + sj + ' questions from the actual ' + ex + ' exam to improve your performance.',
            'Prepare for ' + ex + ' with the official ' + yr + ' ' + sj + ' question paper. Download the PDF and practice from the real exam. Completely free.',
            'Get the ' + ex + ' ' + yr + ' ' + sj + ' PYQ PDF for free. Solve actual exam questions and build confidence for your upcoming ' + ex + ' test.',
        ];
        var idx = Math.abs((ex + sj + yr).split('').reduce(function(a, c) { return a + c.charCodeAt(0); }, 0)) % tmpl.length;
        d.value = tmpl[idx];
        this.textContent = 'Done!';
    });
});
