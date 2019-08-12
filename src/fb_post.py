import time


class FbPost(object):
    VIDEO = 'video'
    IMAGE = 'image'
    """docstring for FbPost"""

    def __init__(self, deviation, **kwargs):
        super(FbPost, self).__init__()
        for key in kwargs:
            if key == 'posted_time':
                self.posted_time = kwargs[key] + deviation
            else:
                setattr(self, key, kwargs[key])
        self.media_path = None
        self.video_id = None

    def set_data(self, **kwargs):
        for key in kwargs:
            if key == 'comment_count' or key == 'share_count' or key == 'reaction_count':
                setattr(self, key, self.convert_to_number(kwargs[key]))
            else:
                setattr(self, key, kwargs[key])
        self.reach_count = (self.priority * ((self.share_count * 2) +
                                             (self.reaction_count) + (self.comment_count * 1.2)))

    def convert_to_number(self, reach_count_str="0"):
        try:
            reach_count_str = reach_count_str.lower()
            if 'k' in reach_count_str or 'వే' in reach_count_str:
                return int(1000 * float(reach_count_str.replace('k', '').replace('వే', '')))
            elif 'm' in reach_count_str:
                return int(1000000 * float(reach_count_str.replace('m', '')))
            else:
                return int(reach_count_str)
        except Valueerror as e:
            log.error(e)
            return 0

    def mark_as_done(self):
        self.completed_time = time.time()

    def get_dict(self):
        return self.__dict__

    def __str__(self):
        return ("Page name : "+self.page_name+"\nImage Src : "+str(self.img_src)+"\nPosted Time : "+str(time.strftime('%m/%d/%Y, %H:%M:%S', time.localtime(self.posted_time)))
                + "\nTime stamp : "+str(self.posted_time)+"\nShare Count : "+str(self.share_count)+"\nComment Count : "+str(self.share_count)+"\nReaction Count : "+str(self.reaction_count) +
                "\nPost Message: "+str(self.post_msg)+"\nReach count :"+str(self.reach_count)+"\nvideo_id : "+str(self.video_id))
