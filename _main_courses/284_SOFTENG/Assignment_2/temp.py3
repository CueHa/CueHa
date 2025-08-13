import sys

def count_inversions(arr):
    tmp = [0] * len(arr)

    def sort_count(l, r):
        if r - l <= 1:
            return 0
        m = (l + r) // 2
        inv = sort_count(l, m) + sort_count(m, r)
        i, j, k = l, m, l
        while i < m and j < r:
            if arr[i] <= arr[j]:
                tmp[k] = arr[i]
                i += 1
            else:
                tmp[k] = arr[j]
                j += 1
                inv += m - i          # all remaining in left half are > arr[j]
            k += 1
        while i < m:
            tmp[k] = arr[i]; i += 1; k += 1
        while j < r:
            tmp[k] = arr[j]; j += 1; k += 1
        arr[l:r] = tmp[l:r]
        return inv

    return sort_count(0, len(arr))

def main():
    data = sys.stdin.read().strip().split()
    n = int(data[0])
    a = list(map(int, data[1:1+n]))
    print(count_inversions(a))

if __name__ == "__main__":
    main()
