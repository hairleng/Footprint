function getUserLogs(user_id) {
    console.log("ajax:" + user_id)
    $.ajax({
        url: "/socialnetwork/get-user-logs/" + user_id,
        dataType: "json",
        success: updatePage,
        error: updateError,
        async: false,
    });
}