'''
Created on 28-APR-2017

@author: Raman
'''
import cv2
import numpy as np 
import math 
import pyglet 
#pyglet.lib.load_library('avbin') 
#pyglet.have_avbin=True
cap = cv2.VideoCapture(0)

# Load and store mp3 files of songs 
a1   = pyglet.media.load('a1.mp3', streaming=False) 
a2   = pyglet.media.load('a2.mp3', streaming=False) 
a3   = pyglet.media.load('a3.mp3', streaming=False) 
a4   = pyglet.media.load('a4.mp3', streaming=False) 
a5   = pyglet.media.load('a5.mp3', streaming=False) 
a6   = pyglet.media.load('a6.mp3', streaming=False) 
a7   = pyglet.media.load('a7.mp3', streaming=False) 
a8   = pyglet.media.load('a8.mp3', streaming=False) 
a9   = pyglet.media.load('a9.mp3', streaming=False) 
a10  = pyglet.media.load('a10.mp3',streaming=False) 


player1 =  pyglet.media.Player() 
player2 =  pyglet.media.Player() 
player3 =  pyglet.media.Player() 
player4 =  pyglet.media.Player() 
player5 =  pyglet.media.Player() 
player6 =  pyglet.media.Player() 
player7 =  pyglet.media.Player() 
player8 =  pyglet.media.Player() 
player9 =  pyglet.media.Player() 
player10 = pyglet.media.Player() 

# Store mp3 file in each of the players 
player1.queue(a1) 
player2.queue(a2) 
player3.queue(a3) 
player4.queue(a4) 
player5.queue(a5) 
player6.queue(a6) 
player7.queue(a7) 
player8.queue(a8) 
player9.queue(a9) 
player10.queue(a10) 

# Create a list of the players 
players = [] 
players.append(player1) 
players.append(player2) 
players.append(player3) 
players.append(player4) 
players.append(player5) 
players.append(player6) 
players.append(player7) 
players.append(player8) 
players.append(player9) 
players.append(player10) 


check = 0      # Checks if the music is currently playing, 0 means not playing 
current = 0    # Keeps track of which song in the list you are on 
gonext = 0     # Keeps track if you have already moved to the next song 
pause = 0      # Keeps track if you have paused the song already 



while True:
    ret, frame = cap.read()    
    if ret==True:    
        frame = cv2.flip(frame,1)
        cv2.imshow('frame',frame)
        #cv2.rectangle(img, pt1, pt2, color[, thickness[, lineType[, shift]]]) 
        cv2.rectangle(frame,(400,400),(100,100),(0,255,0),1)
        crop_img = frame[100:400, 100:400]        
        # Create grayscale version of the image
        grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        value = (33, 33)
        blurred = cv2.GaussianBlur(grey, value, 0)        
        # Threhold the image to make it black and white
        _,thresh1 = cv2.threshold(blurred, 300, 255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        cv2.imshow('Thresholded', thresh1)        
        # Find the contours
        contours, hierarchy = cv2.findContours(thresh1.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        max_area = -1
        for i in range(len(contours)):
            cnt=contours[i]
            area = cv2.contourArea(cnt)
            if(area>max_area):
                max_area=area
                ci=i
        cnt=contours[ci]
        x,y,w,h = cv2.boundingRect(cnt)
        
        # Draw a convex hull
        hull = cv2.convexHull(cnt)
        drawing = np.zeros(crop_img.shape,np.uint8)
        cv2.drawContours(drawing,[cnt],0,(0,255,0),0)
        cv2.drawContours(drawing,[hull],0,(0,0,255),0)
        hull = cv2.convexHull(cnt,returnPoints = False)
        
        # Find the center x and y points of the contours
        M = cv2.moments(cnt)
        centroid_x = int(M['m10']/M['m00'])
        centroid_y = int(M['m01']/M['m00'])
        thex = str(centroid_x)
        they = str(centroid_y)
        center = thex + " " + they
        
        # Find the convexity defects
        defects = cv2.convexityDefects(cnt,hull)
        count_defects = 0
        cv2.drawContours(thresh1, contours, -1, (0,255,0), 3)
        for i in range(defects.shape[0]):
            s,e,f,d = defects[i,0]
            start = tuple(cnt[s][0])
            end = tuple(cnt[e][0])
            far = tuple(cnt[f][0])
            a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
            c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
            angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57
            if angle <= 90:
                count_defects += 1
                cv2.circle(crop_img,far,1,[0,0,255],-1)
            cv2.line(crop_img,start,end,[0,255,0],2)
         
        # If the centroid y value is close enough to the top, increase volume
        if centroid_y < 100:
            cv2.putText(frame,"Volume UP", (200,60), cv2.FONT_HERSHEY_SIMPLEX, 2, 2,2)
            print ("Volume up")

            if players[current].volume < 1:
                players[current].volume += .05
        
        # If the centroid x value is close enough to the left of the screen, pause music
        elif centroid_x < 50:
            cv2.putText(frame,"Pause", (200,60), cv2.FONT_HERSHEY_SIMPLEX, 2, 2,2)
            print ("Pause")

            if pause == 0:
                players[current].pause()
                pause = 1
                check = 0
                 
        # If the centroid x value is far enough to the right, go to the next song
        elif centroid_x > 250:
            cv2.putText(frame,"Go Next", (200,60), cv2.FONT_HERSHEY_SIMPLEX, 2, 2,2)
            print ("Next")

            if gonext == 0:
                players[current].pause()
                current = current + 1
                if current > 3:
                    current = 0
                gonext = 1
                players[current].play()
          
        # If the centroid y value is far down enough, gradually decease the volume
        elif centroid_y > 220:
            cv2.putText(frame,"Volume Down", (200,60), cv2.FONT_HERSHEY_SIMPLEX, 2, 2,2)
            print ("Volume down")
            if players[current].volume > 0:
                players[current].volume -= 0.05
                 
        # If the user spreads their fingers out, play music
        elif count_defects == 4:
            text = "Play music"
            goback = 0
            gonext = 0
            cv2.putText(frame, text, (200,60), cv2.FONT_HERSHEY_SIMPLEX, 2, 2, 2)
            print ("airmouse")
            if check == 0:
                players[current].play()
                check = 1

        elif count_defects == 3:
            text = "Playlist"
            goback = 0
            gonext = 0
            cv2.putText(frame, text, (200,60), cv2.FONT_HERSHEY_SIMPLEX, 2, 2, 2)
            print ("Playlist")
            img = cv2.imread('playlist.jpg', 1)
            cv2.imshow('PlayList', img)
            if check == 0:
                players[current].play()
                check = 1

        elif count_defects == 2:
            text = "Lyrics"
            goback = 0
            gonext = 0
            cv2.putText(frame, text, (200,60), cv2.FONT_HERSHEY_SIMPLEX, 2, 2, 2)
            print ("Lyrics")
            if check == 0:
                players[current].play()
                if players[current]==player1:
                    img = cv2.imread('a1.jpg', 1)
                    cv2.imshow('Lyrics of a1', img)

                check = 1

        else:
            pause = 0
            gonext = 0
            
            cv2.putText(frame,"Hand Gesture", (100,60),\
                    cv2.FONT_HERSHEY_SIMPLEX, 2, 2, 2)
            cv2.putText(frame,"Music Player", (200,100),\
                    cv2.FONT_HERSHEY_SIMPLEX, 2, 2, 2 )
            
            if check == 1:
                if players[current].playing == False:
                    current += current
                    if current > 3:
                        current = 0
                    players[current].play()
       
        cv2.imshow('Gesture', frame)
        all_img = np.hstack((drawing, crop_img))
 
            
        if cv2.waitKey(1) & 0xFF == ord('q'):      #Quit if the user presses q
            break
        
#pyglet.app.run()

# Release everything if job is finished
cap.release()
cv2.destroyAllWindows()

 
if __name__ == '__main__':
    pass