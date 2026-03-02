# MusicAnnotator
An incomplete implementation of a music annotator designed to generate data

The original purpose of this project was to implement an interface similar to that of MuseScore, with the additional capability of being able to annotate data alongside the original song being played. 
The music being played at the same time would allow for annotation to be done much more accurately, allowing for precision in milliseconds.

However, the problem is that with the current method, annotating a song that varies greatly in its pitch (such as Flight of the Bumblebee), will take a large amount of time, as each change in pitch must be accounted for. 
While this annotation tool works, it is far too ineffective to be utilised to generate data quickly. 
