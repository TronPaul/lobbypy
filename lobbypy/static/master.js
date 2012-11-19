var lobbies_s;
var lobby_s;

$(document).ready(function() {
    WEB_SOCKET_SWF_LOCATION = "/static/WebSocketMain.swf";
    WEB_SOCKET_DEBUG = true;

    lobbies_s = io.connect('/lobbies'),
    lobby_s = io.connect('/lobby');

    var LobbyModel = Backbone.Model.extend({
    });

    var LobbyView = Backbone.View.extend({
        events: {
            "click .team-title": "set_team",
            "click .spectator-title": "set_spectator",
            "click #leave": "leave",
            "click .class": "set_class",
            "click #toggle-ready": "toggle_ready",
            "click #start-lobby": "start_lobby",
        },

        set_team: function(evt) {
            evt.preventDefault();

            team_id = $(evt.currentTarget).parent().attr("id").slice(-1);
            lobby_s.emit('set_team', team_id);
        },

        set_class: function(evt) {
            evt.preventDefault();

            class_id = $(evt.currentTarget).attr("id").slice(-1);
            if (class_id == 0) {
                class_id = undefined;
            }
            lobby_s.emit('set_class', class_id);
        },

        set_spectator: function(evt) {
            evt.preventDefault();
            lobby_s.emit('set_team', undefined);
        },

        toggle_ready: function(evt) {
            evt.preventDefault();
            lobby_s.emit('toggle_ready');
        },

        start_lobby: function(evt) {
            evt.preventDefault();
            lobby_s.emit('start');
        },

        leave: function(evt) {
            evt.preventDefault();
            lobby_s.emit('leave');
            window.location.hash = "#";
        },

        initialize: function() {
            var me = this;
            lobby_s.on('destroy', function() {
                me.undelegateEvents();
                window.location.hash = '#';
            });

            lobby_s.on('leave', function() {
                me.undelegateEvents();
                window.location.hash = '#';
            });

            lobby_s.on('update', function(me_lp, lobby) {
                me_lp.is_ready = lobby.is_ready;
                me_lp.is_lock = lobby.lock;
                model = {
                    lobby: lobby,
                    me: me_lp,
                };
                me.model = model;
                me.render();
            });
        },

        render: function() {
            var me = this;

            var template = Handlebars.compile($("#lobby_template").html());

            $.each(this.model.lobby.teams, function(index, value) {
                value.id = index;
            });

            $(this.el).html(template(this.model));

            return this;
        },
    });

    var LobbiesCollection = Backbone.Collection.extend({
        model: LobbyModel
    });

    var LobbiesView = Backbone.View.extend({
        events: {
            "submit #create_lobby_form": "create_lobby",
        },

        create_lobby: function(evt) {
            evt.preventDefault();
            var me = this;

            var lobby_name = $('#lobby_name').val();
            var _hidden_events = {};

            // do ajax create of lobby
            $.ajax({
                url: '/_ajax/lobby/create',
                data: {
                    name: lobby_name
                },
                beforeSend: function() {
                    _hidden_events = lobbies_s.$events;
                    lobbies_s.$events = {};
                },
                success: function(lobby_id) {
                    lobbies_s.emit('unsubscribe');
                    me.undelegateEvents();
                    window.location.hash = '#lobby/' + lobby_id;
                },
                error: function() {
                    lobbies_s.$events = _hidden_events;
                }
            });

            $("#lobby_name").val("");
        },

        initialize: function() {
            var me = this;

            // recieve create signal from server
            lobbies_s.on('create', function(lobby) {
                me.collection.unshift(lobby);
                me.render();
            });

            // recieve destroy signal from server
            lobbies_s.on('destroy', function(lobby_id) {
                lobby_old = me.collection.filter(function(lobby) {
                    lobby.id === lobby_id
                })[0];
                me.collection.pop(lobby_old);
                me.render();
            });

            // recieve lobby update
            lobbies_s.on('update', function(lobby) {
                lobby_old = me.collection.filter(function(lobby_old) {
                    lobby_old.id === lobby.id;
                })[0];
                lobby_old = lobby;
                me.render();
            });

            // recieve update all lobbies
            lobbies_s.on('update_all', function(lobbies) {
                me.collection = lobbies;
                me.render();
            });
        },

        render: function() {
            var me = this;

            var template = Handlebars.compile($("#lobbies_template").html());

            $(this.el).html(template({lobbies: this.collection}));

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
            var view = new LobbiesView({
                el: $("#container"),
                collection: [],
            });
            view.render();
            // connect to the websocket
            lobbies_s.emit('subscribe');
        },

        // View a lobby
        lobby: function(lobby_id) {
            var view = new LobbyView({
                el: $("#container"),
                model: {},
            });

            // join lobby
            lobbies_s.emit('unsubscribe');
            lobby_s.emit('join', lobby_id);
        },
    });

    // start backbone routing
    var app = new Router();
    Backbone.history.start();
});
