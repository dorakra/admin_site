 /* collapsed_stacked_inlines.js */
/* Created in May 2009 by Hannes Rydén */
/* Use, distribute and modify freely */

// Original script
// https://djangosnippets.org/snippets/1492/

// 2021 updates by Dimitris Karagiannis
// @MitchKarajohn
// https://djangosnippets.org/snippets/10817/

// 2023 updates by Dmitry Akinin
// https://djangosnippets.org/snippets/10947/

/* stacked inline elemeket osszecsukhatova tesz */

/* az add gomb megnyomasakor is lefut */
/* ehhez kesleltetes kell, mert a div.row-add-et az inlines.js hozza letre, nincs meg az oldal betoltesekor */

function waitAddRow() {
    const el = document.querySelector('.inline-group div.add-row a');

    if (el != null) {
        $('.inline-group div.add-row a').click(function() {
            collapseItems();
        });
    } 
    else {
        setTimeout(waitAddRow, 200); // try again in 200 milliseconds
    }
}

jQuery(function ($) {

    collapseItems();
    waitAddRow();

});

function collapseItems() {

  //var linkStyle ='cursor: pointer; color: #fff; border-radius: 4px; font-weight: 400; padding: 5px 10px; background: #417690; border: none;'; - ez a base.css-be kerult

  $('div.inline-group div.inline-related:not(.empty-form, .tabular)').each(function () {

        const $h3 = $(this.querySelector('h3'));
        const $fs = $(this.querySelector('fieldset:not(.stacked_collapse)')); //csak azokat a fieldseteket modositja, amiket meg nem
        const fsErrorsExist = $fs.children('.errors').length;
        const initialButtonText = fsErrorsExist ? gettext('Hide') : gettext('Show');
        const $button = $(
          $.parseHTML(
            '<a role="button"' + 
              //' style="' + linkStyle +
              '" class="stacked_collapse-toggle">' +
              initialButtonText +
              '</a> '
          )

        );

        // Don't collapse initially if fieldset contains errors
        if (fsErrorsExist) $fs.addClass('stacked_collapse');
        else $fs.addClass('stacked_collapse collapsed');

        // Add toggle link
        //$button.click(function () {
          //if (!$fs.hasClass('collapsed')) {
            //$fs.addClass('collapsed');
            //this.innerHTML = gettext('Show');
          //} else {
            //$fs.removeClass('collapsed');
            //this.innerHTML = gettext('Hide');
          //}
        //});

        if ($(this.querySelector('h3 a:not(.inline-deletelink)')).length == 0) {
            $h3.prepend($button); //csak akkor rakja ki a gombot, ha meg nincs
        }
        // Hide/Show button click
        $button.click(function () {
            const $fs = $(this).parents('.inline-related').children('fieldset')
            if (!$fs.hasClass('collapsed')) {
              $fs.addClass('collapsed');
              this.innerHTML = gettext('Show');
            } else {
              $fs.removeClass('collapsed');
              this.innerHTML = gettext('Hide');
            }
        });

  });
    
}
