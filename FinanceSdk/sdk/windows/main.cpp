
#include "WeWorkFinanceSdk_C.h"

#pragma comment(lib, "WeWorkFinanceSdk.lib")

int main(int argc, char* argv[]) {
	auto sdk = NewSdk();
	int ret = Init(sdk, nullptr, nullptr);

	Slice_t sli;
	ret = GetChatData(sdk, 100, 100, nullptr, nullptr, 100, &sli);
	DecryptData(nullptr, sli.buf, &sli);
	MediaData_t *data = nullptr;
	GetMediaData(sdk,nullptr, nullptr, nullptr, "123", 50, data);

	Slice_t *psli = NewSlice();
	FreeSlice(psli);
	GetContentFromSlice(psli);
	NewMediaData();

	GetData(data);
	GetOutIndexBuf(data);
	IsMediaDataFinish(data);
	FreeMediaData(data);
	
	
	

	DestroySdk(sdk);

	return 0;
}
