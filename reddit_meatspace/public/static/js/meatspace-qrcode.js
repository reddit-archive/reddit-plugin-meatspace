r.meatspace = {
    init: function () {
        var container = $('#badge .qrcode'),
            placeholder = container.find('.placeholder'),
            uri = placeholder.data('url')

        if (!placeholder.length)
            return

        placeholder.qrcode({
            width: 230,
            height: 230,
            text: uri
        })
    }
}

r.meatspace.init()
