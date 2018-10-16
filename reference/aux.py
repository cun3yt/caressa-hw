import vlc


media_player_events = [
    vlc.EventType.MediaPlayerMediaChanged,
    vlc.EventType.MediaPlayerNothingSpecial,
    vlc.EventType.MediaPlayerOpening,
    vlc.EventType.MediaPlayerBuffering,
    vlc.EventType.MediaPlayerPlaying,
    vlc.EventType.MediaPlayerPaused,
    vlc.EventType.MediaPlayerStopped,
    vlc.EventType.MediaPlayerForward,
    vlc.EventType.MediaPlayerBackward,
    vlc.EventType.MediaPlayerEndReached,
    vlc.EventType.MediaPlayerEncounteredError,
    vlc.EventType.MediaPlayerTimeChanged,
    vlc.EventType.MediaPlayerPositionChanged,
    vlc.EventType.MediaPlayerSeekableChanged,
    vlc.EventType.MediaPlayerPausableChanged,
    vlc.EventType.MediaPlayerTitleChanged,
    vlc.EventType.MediaPlayerSnapshotTaken,
    vlc.EventType.MediaPlayerLengthChanged,
    vlc.EventType.MediaPlayerVout,
    vlc.EventType.MediaPlayerScrambledChanged,
    vlc.EventType.MediaPlayerESAdded,
    vlc.EventType.MediaPlayerESDeleted,
    vlc.EventType.MediaPlayerESSelected,
    vlc.EventType.MediaPlayerCorked,
    vlc.EventType.MediaPlayerUncorked,
    vlc.EventType.MediaPlayerMuted,
    vlc.EventType.MediaPlayerUnmuted,
    vlc.EventType.MediaPlayerAudioVolume,
    vlc.EventType.MediaPlayerAudioDevice,
    vlc.EventType.MediaPlayerChapterChanged,
]


events = [vlc.EventType.MediaMetaChanged,
          vlc.EventType.MediaSubItemAdded,
          vlc.EventType.MediaDurationChanged,
          vlc.EventType.MediaParsedChanged,
          vlc.EventType.MediaFreed,

          vlc.EventType.MediaStateChanged,
          vlc.EventType.MediaSubItemTreeAdded,

          vlc.EventType.MediaPlayerMediaChanged,
          vlc.EventType.MediaPlayerNothingSpecial,
          vlc.EventType.MediaPlayerOpening,
          vlc.EventType.MediaPlayerBuffering,
          vlc.EventType.MediaPlayerPlaying,
          vlc.EventType.MediaPlayerPaused,
          vlc.EventType.MediaPlayerStopped,
          vlc.EventType.MediaPlayerForward,
          vlc.EventType.MediaPlayerBackward,
          vlc.EventType.MediaPlayerEndReached,
          vlc.EventType.MediaPlayerEncounteredError,
          vlc.EventType.MediaPlayerTimeChanged,
          vlc.EventType.MediaPlayerPositionChanged,
          vlc.EventType.MediaPlayerSeekableChanged,
          vlc.EventType.MediaPlayerPausableChanged,
          vlc.EventType.MediaPlayerTitleChanged,
          vlc.EventType.MediaPlayerSnapshotTaken,
          vlc.EventType.MediaPlayerLengthChanged,
          vlc.EventType.MediaPlayerVout,
          vlc.EventType.MediaPlayerScrambledChanged,
          vlc.EventType.MediaPlayerESAdded,
          vlc.EventType.MediaPlayerESDeleted,
          vlc.EventType.MediaPlayerESSelected,
          vlc.EventType.MediaPlayerCorked,
          vlc.EventType.MediaPlayerUncorked,
          vlc.EventType.MediaPlayerMuted,
          vlc.EventType.MediaPlayerUnmuted,
          vlc.EventType.MediaPlayerAudioVolume,
          vlc.EventType.MediaPlayerAudioDevice,
          vlc.EventType.MediaPlayerChapterChanged,

          vlc.EventType.MediaListItemAdded,             # playlist event
          vlc.EventType.MediaListWillAddItem,           # playlist event
          vlc.EventType.MediaListItemDeleted,           # unknown
          vlc.EventType.MediaListWillDeleteItem,        # unknown
          vlc.EventType.MediaListEndReached,            # unsupported
          vlc.EventType.MediaListViewItemAdded,         # unknown
          vlc.EventType.MediaListViewWillAddItem,       # unknown
          vlc.EventType.MediaListViewItemDeleted,       # unknown
          vlc.EventType.MediaListViewWillDeleteItem,    # unknown
          vlc.EventType.MediaListPlayerPlayed,          # player event => when song ends?
          vlc.EventType.MediaListPlayerNextItemSet,     # player event => this is when song starts from beginning
          vlc.EventType.MediaListPlayerStopped,

          vlc.EventType.MediaDiscovererStarted,
          vlc.EventType.MediaDiscovererEnded,

          vlc.EventType.RendererDiscovererItemAdded,    # unsupported?
          vlc.EventType.RendererDiscovererItemDeleted,  # unsupported?

          vlc.EventType.VlmMediaAdded,
          vlc.EventType.VlmMediaRemoved,
          vlc.EventType.VlmMediaChanged,

          vlc.EventType.VlmMediaInstanceStarted,
          vlc.EventType.VlmMediaInstanceStopped,
          vlc.EventType.VlmMediaInstanceStatusInit,
          vlc.EventType.VlmMediaInstanceStatusOpening,
          vlc.EventType.VlmMediaInstanceStatusPlaying,
          vlc.EventType.VlmMediaInstanceStatusPause,
          vlc.EventType.VlmMediaInstanceStatusEnd,
          vlc.EventType.VlmMediaInstanceStatusError,
]

# playlist_em = self._playlist.event_manager()
# for event in events:
#     playlist_em.event_attach(event, lambda ev: print("  PLAYLIST EVENT!!!: this is happening: {}".format(ev)))
#     player_event_manager.event_attach(event, lambda ev: print("  PLAYER EVENT!!!: this is happening: {}".format(ev)))
