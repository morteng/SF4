$(document).ready(function() {
    $('.edit-stipend').click(function(e) {
        e.preventDefault();
        var stipendId = $(this).data('id');
        $.ajax({
            url: `/admin/stipends/${stipendId}/edit`,
            method: 'GET',
            success: function(response) {
                $('#modal-content').html(response);
                $('#editModal').modal('show');
            },
            error: function(error) {
                alert("Failed to load edit form.");
            }
        });
    });

    $('.edit-organization').click(function(e) {
        e.preventDefault();
        var organizationId = $(this).data('id');
        $.ajax({
            url: `/admin/organizations/${organizationId}/edit`,
            method: 'GET',
            success: function(response) {
                $('#modal-content').html(response);
                $('#editModal').modal('show');
            },
            error: function(error) {
                alert("Failed to load edit form.");
            }
        });
    });

    $('.edit-bot').click(function(e) {
        e.preventDefault();
        var botId = $(this).data('id');
        $.ajax({
            url: `/admin/bots/${botId}/edit`,
            method: 'GET',
            success: function(response) {
                $('#modal-content').html(response);
                $('#editModal').modal('show');
            },
            error: function(error) {
                alert("Failed to load edit form.");
            }
        });
    });

    $('.edit-tag').click(function(e) {
        e.preventDefault();
        var tagId = $(this).data('id');
        $.ajax({
            url: `/admin/tags/${tagId}/edit`,
            method: 'GET',
            success: function(response) {
                $('#modal-content').html(response);
                $('#editModal').modal('show');
            },
            error: function(error) {
                alert("Failed to load edit form.");
            }
        });
    });
});
