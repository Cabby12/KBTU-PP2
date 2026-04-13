import pygame
import os

class MusicPlayer:
    def __init__(self, music_folder):
        pygame.mixer.init()
        self.music_folder = music_folder
        self.tracks = []
        self.current = 0
        self.playing = False
        self.stopped = False
        self.font = pygame.font.SysFont("arial", 22)
        self.small = pygame.font.SysFont("arial", 16)
        self.load_tracks()

    def load_tracks(self):
        if not os.path.exists(self.music_folder):
            os.makedirs(self.music_folder)
        for f in os.listdir(self.music_folder):
            if f.endswith(".mp3") or f.endswith(".wav"):
                self.tracks.append(os.path.join(self.music_folder, f))
        self.tracks.sort()

    def play(self):
        if len(self.tracks) == 0:
            print("no tracks found in music/ folder")
            return
        if self.stopped:
            pygame.mixer.music.unpause()
            self.stopped = False
        elif not self.playing:
            pygame.mixer.music.load(self.tracks[self.current])
            pygame.mixer.music.play()
        self.playing = True

    def stop(self):
        pygame.mixer.music.pause()
        self.playing = False
        self.stopped = True

    def next_track(self):
        if len(self.tracks) == 0:
            return
        self.current = (self.current + 1) % len(self.tracks)
        self.playing = False
        self.stopped = False
        self.play()

    def prev_track(self):
        if len(self.tracks) == 0:
            return
        self.current = (self.current - 1) % len(self.tracks)
        self.playing = False
        self.stopped = False
        self.play()

    def update(self):
        if self.playing and not pygame.mixer.music.get_busy():
            self.next_track()

    def draw(self, screen):
        screen.fill((30, 30, 30))

        title = self.font.render("Music Player", True, (255, 255, 255))
        screen.blit(title, (20, 20))

        if len(self.tracks) == 0:
            msg = self.small.render("no tracks in music/ folder", True, (200, 100, 100))
            screen.blit(msg, (20, 80))
        else:
            track_name = os.path.basename(self.tracks[self.current])
            t = self.small.render(f"track: {track_name}", True, (180, 220, 180))
            screen.blit(t, (20, 70))

            num = self.small.render(f"{self.current + 1} / {len(self.tracks)}", True, (150, 150, 150))
            screen.blit(num, (20, 100))

        status = "playing" if self.playing else "stopped"
        color = (100, 255, 100) if self.playing else (255, 100, 100)
        s = self.small.render(f"status: {status}", True, color)
        screen.blit(s, (20, 140))

        pos = pygame.mixer.music.get_pos()
        if pos > 0:
            secs = pos // 1000
            pos_text = self.small.render(f"position: {secs}s", True, (150, 150, 255))
            screen.blit(pos_text, (20, 165))

        controls = [
            "P = play",
            "S = stop",
            "N = next",
            "B = prev",
            "Q = quit"
        ]
        for i, c in enumerate(controls):
            ct = self.small.render(c, True, (200, 200, 200))
            screen.blit(ct, (320, 70 + i * 25))
