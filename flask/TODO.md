- get all games a contestant has played
- get clues by game id
- get clues by game date

**Web with updated cluebase clues**
- parse games, handling dj, fj, and unseen clues, and links,
- show clues in web, handle score + showing clue / correct / incorrect
- handle going to next round after all clues have been revealed
- handle going to final jeopardy clue
- create tables for practice player and practice games
- track score, num correct, num incorrect, num buzzed, num seen, celerity, fj correct or incorrect, and a game summary json that we can use to further analyze the game
- show if you've played a game before or not with that player
- show their most recent score and celerity on game select screen
- create a game history page that shows all of the above

**Buzzing**
- when clue is opened read clue text and press button or space to start timer
  - send signal to buzzer 
  - start a timer, when timer is up, play audio and show button for "no answer", and send signal to buzzer
  - if buzzer sends signal back before time is over, show buttons for "correct" and "incorrect", and track celerity
- for daily double, play an audio when clue is opened, but otherwise the same as above
- for final jeopardy no buzzer
- buzzer logic can be much simplified in arduino land since we'll handle the audio. It only needs to track buzzer timing, sending a signal to the computer when buzzer is pressed, handling penalties, and showing lights when player can buzz in

download and parse all contestants

fix contestants unique constraint (should be by name + jarchive id)
fix contestants games_played? idk if I should set it back to non-nullable or not...
potentially don't need pased_games episode_num uniqueness either
fix old archived games by hand at some point