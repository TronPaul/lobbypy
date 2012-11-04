var socket;

$(document).ready(function() {
    WEB_SOCKET_SWF_LOCATION = "/static/WebSocketMain.swf";
    WEB_SOCKET_DEBUG = true;

    var LobbyModel = Backbone.Model.extend({
    });

    var LobbyView = Backbone.View.extend({
        initialize: function() {
            // rerender on change
            this.model.bind('change', this.render);
        },

        render: function() {
            var template = Handlebars.compile($("#lobby_template").html());

            this.$el.html(template(this.model.toJSON()));

            return this;
        }
    });

    var LobbiesCollection = Backbone.Collection.extend({
        model: LobbyModel
    });

    var LobbiesView = Backbone.View.extend({
        events: {
            "submit #create_lobby_form": "create_lobby",
        },

        create_lobby: function(evt) {
            evt.preventDefault()

            var lobby_name = $('#lobby_name').val();

            // do ajax create of lobby
            $.ajax({
                url: '/_ajax/lobby/create',
                data: {
                    name: lobby_name
                },
                error: function(jqXHR) {
                },
                success: function(data, textStatus) {
                },
            });

            $("#lobby_name").val("");
        },

        initialize: function() {
            var me = this;

            // recieve create signal from server
            socket.on('create', function(lobby) {
                var lobby_item = new LobbyView({
                    model: new LobbyModel({
                        lobby: lobby
                    })
                });

                // render it to the DOM
                el = lobby_item.render().el;
                me.$("#lobbies").append(el);
            });

            // recieve destroy signal from server
            socket.on('destroy', function(lobby_id) {
            });

            // recieve lobby update
            socket.on('update', function(lobby_id, lobby_info) {
            });
        },

        render: function() {
            var me = this;

            var template = Handlebars.compile($("#lobbies_template").html());

            $(this.el).html(template());

            return this;
        },
    });

    // Backbone.js router
    var Router = Backbone.Router.extend({
        // Match urls with methods
        routes: {
            "": "index",
            "lobby/:lobby_id": "lobby",
        },

        index: function() {
            // get lobbies via ajax
            $.ajax({
                url: '/_ajax/lobby/all',
                success: function(data) {
                },});
            // connect to the websocket
            socket = io.connect('/lobbies');
            socket.emit('subscribe');
            var view = new LobbiesView({
                el: $("#container"),
            });

            view.render();
        },

        // View a lobby
        lobby: function(lobby_id) {
            alert('Viewing lobby' + lobby_id);
        },
    });

    // start backbone routing
    var app = new Router();
    Backbone.history.start({ pushState: true });
});
