var lobbies_s;
var lobby_s;

$(document).ready(function() {
    WEB_SOCKET_SWF_LOCATION = "/static/WebSocketMain.swf";
    WEB_SOCKET_DEBUG = true;

    lobbies_s = io.connect('/lobbies'),
    lobby_s = io.connect('/lobby');

    var classes = {
        1: 'scout',
        2: 'soldier',
        3: 'pyro',
        4: 'heavy',
        5: 'demoman',
        6: 'engineer',
        7: 'medic',
        8: 'sniper',
        9: 'spy',
    }

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

            lobby_s.on('start', function(password) {
                alert('Lobby started w/ password: ' + password);
                // TODO: redirect to match page
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
            "click #show-create-lobby": "show_create_lobby_form",
            "click .lobby-item": "join_lobby",
        },

        join_lobby: function(evt) {
            evt.preventDefault();
            lobby_id = $(evt.currentTarget).attr("id").slice(-1);
            this.undelegateEvents();
            window.location.hash = '#/lobby/' + lobby_id;
        },

        show_create_lobby_form: function(evt) {
            evt.preventDefault();
            var form_view = new CreateLobbyFormView({
                el: $('#pop-up'),
            });
            $('#show-create-lobby').attr('disabled', 'disabled');
            form_view.render();
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
                lobby.open_classes = _.map(lobby.open_classes, function(cls) {
                    return classes[cls];
                });
                lobby_old = me.collection.filter(function(lobby_old) {
                    lobby_old.id === lobby.id;
                })[0];
                lobby_old = lobby;
                me.render();
            });

            // recieve update all lobbies
            lobbies_s.on('update_all', function(lobbies) {
                _.each(lobbies, function(lobby) {
                    lobby.open_classes = _.map(lobby.open_classes, function(cls) {
                        return classes[cls];
                    });
                });
                me.collection = lobbies;
                me.render();
            });
        },

        render: function() {
            var me = this;

            var template = Handlebars.compile($("#lobbies_template").html());

            player = $("#create_lobby_form").length != 0;

            $(this.el).html(template({lobbies: this.collection, player: player}));

            return this;
        },
    });

    var CreateLobbyFormView = Backbone.View.extend({
        events: {
            "click #cancel-create": "hide_create_lobby_form",
            "submit #create-lobby-form": "create_lobby",
        },

        hide_create_lobby_form: function(evt) {
            evt.preventDefault();
            $(this.el).html('');
            $('#show-create-lobby').removeAttr('disabled');
            this.undelegateEvents();
        },

        create_lobby: function(evt) {
            evt.preventDefault();
            var me = this;

            var lobby_name = $('#lobby_name').val();
            var rcon_server = $('#rcon_server').val();
            var rcon_pass = $('#rcon_pass').val();
            var map = $('#map').val();
            var _hidden_events = {};

            // do ajax create of lobby
            $.ajax({
                url: '/_ajax/lobby/create',
                data: {
                    name: lobby_name,
                    rcon_server: rcon_server,
                    rcon_pass: rcon_pass,
                    game_map: map,
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

        render: function() {
            var template = Handlebars.compile($("#create_lobby_form").html());
            $(this.el).html(template());
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
            // TODO: if lobby DNE redirect to index
        },
    });

    // start backbone routing
    var app = new Router();
    Backbone.history.start();
});
