import vlc


urls = ['https://s3-us-west-1.amazonaws.com/caressa-prod/song-set/World/Zamfir/08+La+Valse+Muzeta.mp3',]

Instance = vlc.Instance()
_player = Instance.media_list_player_new()
playlist = Instance.media_list_new(urls)
_player.set_media_list(playlist)
_player.play()

# dynamically adding a new item to the playlist:
playlist.add_media('https://s3-us-west-1.amazonaws.com/caressa-prod/song/alternative/alanis-morissette/Alanis+Morissette+-+Head+Over+Feet.mp3')


# MediaPlayer.audio_get_track_count
# MediaList.count()
# MediaPlayer.get_title

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
          vlc.EventType.MediaListItemAdded,
          vlc.EventType.MediaListWillAddItem,
          vlc.EventType.MediaListItemDeleted,
          vlc.EventType.MediaListWillDeleteItem,
          vlc.EventType.MediaListEndReached,
          vlc.EventType.MediaListViewItemAdded,
          vlc.EventType.MediaListViewWillAddItem,
          vlc.EventType.MediaListViewItemDeleted,
          vlc.EventType.MediaListViewWillDeleteItem,
          vlc.EventType.MediaListPlayerPlayed,
          vlc.EventType.MediaListPlayerNextItemSet,
          vlc.EventType.MediaListPlayerStopped,
          vlc.EventType.MediaDiscovererStarted,
          vlc.EventType.MediaDiscovererEnded,
          vlc.EventType.RendererDiscovererItemAdded,
          vlc.EventType.RendererDiscovererItemDeleted,
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
          vlc.EventType.VlmMediaInstanceStatusError, ]

event_manager = vlc.EventManager()
event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, lambda x: print("  EVENT: this is happening: {}".format(x)))

Instance.vlm_del_media('name of media')

# list_player.next()
# list_player.previous()
# list_player.pause()

