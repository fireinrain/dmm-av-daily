if __name__ == '__main__':
    image_urls = ['baid.com','xiaoqian.com']
    sample_images_tags = [f'<img src="{d}">' for i, d in enumerate(image_urls) if i != 0]
    print(sample_images_tags)
    a = 'abc'
    print(a.split(' '))
    b = ['']
    print(' '.join(b))