function getQuery(q) {
    return (window.location.search.match(new RegExp('[?&]' + q + '=([^&]+)')) || [, null])[1];
}
$(function () {
    var Type = getQuery("type")
    var code = getQuery("code")
    var csrftoken = $('input[name="csrfmiddlewaretoken"]').val();
    var wxID = "";
    $.ajax({
        url: "/checkCode",
        type: "post",
        data: {
            "code": code,
            "type": Type,
            "csrfmiddlewaretoken": csrftoken
        },
        success: function (data) {
            var res = JSON.parse(data);
            if (res.error)
                location.href = "/error"
            else if (res.noBind)
                location.href = "/bind/ctips"
            else if (res.wxID) {
                wxID = res.wxID
                $("#cancel").fadeToggle();
            }
            else
                location.href = "/index"
        }
    });
    $("#cancelBinding").click(function () {
        $("#cancel").fadeToggle();
        var json = {
            "wxID": wxID,
            "type": Type,
            "csrfmiddlewaretoken": csrftoken
        };
        $.ajax({
            url: "/bind/cancel",
            type: "post",
            data: json,
            success: function (data) {
                var res = JSON.parse(data);
                if (res.success)
                    if (res.success == "0")
                        location.href = "/error"
                    else
                        location.href = "/bind/success?type=" + Type
                else {
                    location.href = "/index"
                }
            }
        })
    });

})