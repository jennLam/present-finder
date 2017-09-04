def get_zeros(nums):

    low = 0
    high = len(nums) - 1

    pointer = (low + high) / 2

    if len(nums) == 0:
        return 0

    if nums[low] != 0:
        return 0

    if nums[high] != 1:
        return len(nums)

    while nums[pointer] == nums[pointer + 1]:
        if nums[pointer] == 0 and nums[pointer + 1] == 0:
            low = pointer
            pointer = (low + high) / 2
        if nums[pointer] == 1 and nums[pointer + 1] == 1:
            high = pointer
            pointer = (low + high)/2

    return pointer + 1
