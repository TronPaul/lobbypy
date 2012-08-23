
def make_lobby_player_delta(new_lobby_players, old_lobby_players):
    delta_dict = {}
    mod_or_new = set(new_lobby_players) - set(old_lobby_players)
    removed = (set(map(lambda x: x.player, old_lobby_players)) -
            set(map(lambda x: x.player, new_lobby_players)))
    modified = dict([(mlp.player, mlp) for mlp in filter(lambda x: x.player in [lp.player for lp in old_lobby_players], mod_or_new)])
    new = dict([(nlp.player, nlp) for nlp in filter(lambda x: x not in [p for p in modified.keys()], mod_or_new)])
    def get_only_delta(lp_new, lp_old):
        mod_dict = {'name':lp_new.player.name}
        if lp_new.team != lp_old.team:
            mod_dict['team'] = lp_new.team
        elif lp_new.pclass != lp_old.pclass:
            mod_dict['class'] = lp_new.pclass
        return mod_dict
    delta_dict['modified'] = dict(map(lambda x: (str(x.player.id), get_only_delta(new[x], modified[x])), modified.keys()))
    delta_dict['removed'] = [str(p.id) for p in removed]
    delta_dict['modified'].update(dict([(str(lp.player.id), {'name':lp.player.name, 'team':lp.team, 'class':lp.pclass}) for lp in new.values()]))
    return delta_dict
