$(document).ready(function() {
    $('#id_city').on('input', function() {
        let query = $(this).val();
        if (query.length > 2) {
            $.ajax({
                url: '/autocomplete/',
                data: { q: query },
                success: function(data) {
                    let suggestions = data;
                    $('#suggestions').empty();
                    if (suggestions.length) {
                        suggestions.forEach(function(suggestion) {
                            $('#suggestions').append('<div class="suggestion-item">' +
                                suggestion.city + ' (' + suggestion.city_rus + ')</div>');
                        });
                        $('.suggestion-item').on('click', function() {
                            $('#id_city').val($(this).text().split(' (')[0]);
                            $('#suggestions').empty();
                        });
                    }
                }
            });
        } else {
            $('#suggestions').empty();
        }
    });

    $(document).on('click', function(e) {
        if (!$(e.target).closest('#suggestions, #id_city').length) {
            $('#suggestions').empty();
        }
    });

    if (document.querySelector('.weather-info')) {
        document.querySelector('.back-button').style.display = 'block';
    }
});
