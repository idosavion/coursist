$(document).ready(function () {
    $('#program_input').keypress(function (e) {
        if (e.keyCode === 13) {
            e.preventDefault();
            $('#search_btn').click();
        }
    });
});

class ProgramsLogic {
    constructor() {
        this.programs = {};
    }

    addProgram(program) {
        this.programs[program['code']] = {
            'program': program
        };
    }

    hasProgram(program) {
        return program['code'] in this.programs;
    }

    // hasCourse(course) {
    //     return course['course_number'] in this.courses;
    // }

    getProgramNameByCode(programCode) {
        return this.programs[programCode]['program']['name'];
    }

    removeProgram(code) {
        delete this.programs[code];
    }
}

let programsLogic = new ProgramsLogic();

/**
 * Autocompletes the user search.
 */
function programs_autocomplete(search_val, csrf) {
    let container = $('#search_results');

    if (search_val.length < 2) {
        container.html('');
        return;
    }

    container.html(
        '<div class="text-center">' +
        '<div class="spinner-grow text-primary" role="status"></div>' +
        '</div>'
    );

    ajax({'search_val': search_val},
        (response) => {
            if (response.status !== 'success') {
                container.html('Error, try again.');
                return;
            }

            container.html('<ul></ul>');
            let programs = response.programs;
            if (programs.length === 0) {
                container.html();
                return;
            }

            // display the results
            let list = container.find('ul');
            $.each(programs, function (index, value) {
                if (!programsLogic.hasProgram(value)) {
                    const item_html = hb_templates['degree-program-autocomplete-item']({'program': value});
                    list.append(item_html);
                    $('#add_program_' + value['code']).click(function (e) {
                        e.preventDefault();
                        addProgram(value, csrf);
                        list.html('');
                        $('#program_input').val('');
                    });
                }
            });
        }, () => {
            container.html('Error, try again.');
        });
}

/**
 * Adds a program to the programs list.
 */
function addProgram(program, csrf) {
    console.log(program);
    if (programsLogic.hasProgram(program)) {
        return;
    }

    $.ajax({
        method: 'POST',
        url: './',
        data: {
            csrfmiddlewaretoken: csrf,
            'code': program['code']
        },
        success: function (response) {
            // const groups = response.groups;
            // if (groups.length === 0) {
            //     // TODO show to the user error message?
            //     return;
            // }
            programsLogic.addProgram(program);
            let code = program['code'];
            let program_list_container = $('#my_programs_list');
            let item_html = hb_templates['degree-program-item']({'program': program});
            program_list_container.append(item_html);

            // collapse functionality
            $('#program_item_' + code).find('.program_name').click(function () {
                toggleProgramItem($(this));
            });

            // delete functionality
            $('#del_btn_' + code).click(function () {
                programsLogic.removeProgram(code);
                $('#program_item_' + code).remove();
            });
        },
        error: function () {
            alert('failed');
        }
    });
}

function toggleProgramItem($title_element) {
    if ($title_element.hasClass('opened')) {
        $title_element.removeClass('opened');
    } else {
        $title_element.addClass('opened');
    }
}